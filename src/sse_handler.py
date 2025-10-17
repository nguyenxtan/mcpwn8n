"""
SSE (Server-Sent Events) Handler for MCP protocol
Manages SSE connections and message streaming
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from sse_starlette.sse import ServerSentEvent

from mcp_protocol import MCPProtocolHandler
from models import SSEConfig

logger = logging.getLogger(__name__)


class SSEConnectionManager:
    """
    Manages SSE connections for MCP protocol
    """

    def __init__(self, sse_config: SSEConfig):
        self.config = sse_config
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

        logger.info(
            f"SSE Connection Manager initialized "
            f"(max_connections: {sse_config.max_connections})"
        )

    async def add_connection(self, connection_id: str) -> None:
        """Add a new SSE connection"""
        async with self._lock:
            if len(self.active_connections) >= self.config.max_connections:
                raise Exception(
                    f"Max connections reached ({self.config.max_connections})"
                )

            self.active_connections[connection_id] = {
                "id": connection_id,
                "connected_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow(),
                "messages_sent": 0
            }

            logger.info(
                f"Connection added: {connection_id} "
                f"(total: {len(self.active_connections)})"
            )

    async def remove_connection(self, connection_id: str) -> None:
        """Remove an SSE connection"""
        async with self._lock:
            if connection_id in self.active_connections:
                conn_info = self.active_connections.pop(connection_id)
                duration = (datetime.utcnow() - conn_info["connected_at"]).total_seconds()

                logger.info(
                    f"Connection removed: {connection_id} "
                    f"(duration: {duration:.1f}s, messages: {conn_info['messages_sent']}, "
                    f"remaining: {len(self.active_connections)})"
                )

    async def update_heartbeat(self, connection_id: str) -> None:
        """Update last heartbeat time for a connection"""
        async with self._lock:
            if connection_id in self.active_connections:
                self.active_connections[connection_id]["last_heartbeat"] = datetime.utcnow()

    async def increment_messages(self, connection_id: str) -> None:
        """Increment message counter for a connection"""
        async with self._lock:
            if connection_id in self.active_connections:
                self.active_connections[connection_id]["messages_sent"] += 1

    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        return self.active_connections.get(connection_id)

    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active connections"""
        return self.active_connections.copy()


class SSEHandler:
    """
    SSE Handler for MCP protocol communication
    """

    def __init__(
        self,
        mcp_handler: MCPProtocolHandler,
        connection_manager: SSEConnectionManager,
        sse_config: SSEConfig
    ):
        self.mcp_handler = mcp_handler
        self.connection_manager = connection_manager
        self.config = sse_config

        logger.info("SSE Handler initialized")

    async def handle_sse_connection(
        self,
        connection_id: Optional[str] = None
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """
        Handle SSE connection and stream MCP messages

        Args:
            connection_id: Optional connection ID (will be generated if not provided)

        Yields:
            ServerSentEvent objects
        """
        # Generate connection ID if not provided
        if connection_id is None:
            connection_id = str(uuid4())

        try:
            # Add connection to manager
            await self.connection_manager.add_connection(connection_id)

            # Send initial connection event
            yield ServerSentEvent(
                data=json.dumps({
                    "type": "connection",
                    "connection_id": connection_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "server_info": self.mcp_handler.get_server_info()
                }),
                event="connection"
            )

            await self.connection_manager.increment_messages(connection_id)

            # Create queues for bidirectional communication
            incoming_queue: asyncio.Queue = asyncio.Queue()
            outgoing_queue: asyncio.Queue = asyncio.Queue()

            # Start heartbeat task
            heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(connection_id, outgoing_queue)
            )

            # Start message processing task
            processor_task = asyncio.create_task(
                self._process_incoming_messages(incoming_queue, outgoing_queue)
            )

            try:
                # Stream messages from outgoing queue
                async for event in self._stream_messages(connection_id, outgoing_queue):
                    yield event

            finally:
                # Cleanup tasks
                heartbeat_task.cancel()
                processor_task.cancel()

                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

                try:
                    await processor_task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            logger.error(f"SSE connection error for {connection_id}: {e}", exc_info=True)
            yield ServerSentEvent(
                data=json.dumps({
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }),
                event="error"
            )

        finally:
            # Remove connection from manager
            await self.connection_manager.remove_connection(connection_id)

    async def _heartbeat_loop(
        self,
        connection_id: str,
        outgoing_queue: asyncio.Queue
    ) -> None:
        """
        Send periodic heartbeat messages

        Args:
            connection_id: Connection ID
            outgoing_queue: Queue for outgoing messages
        """
        while True:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)

                # Send heartbeat
                heartbeat = ServerSentEvent(
                    data=json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    event="heartbeat"
                )

                await outgoing_queue.put(heartbeat)
                await self.connection_manager.update_heartbeat(connection_id)

                logger.debug(f"Heartbeat sent to {connection_id}")

            except asyncio.CancelledError:
                logger.debug(f"Heartbeat loop cancelled for {connection_id}")
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {connection_id}: {e}")

    async def _process_incoming_messages(
        self,
        incoming_queue: asyncio.Queue,
        outgoing_queue: asyncio.Queue
    ) -> None:
        """
        Process incoming MCP messages

        Args:
            incoming_queue: Queue for incoming messages
            outgoing_queue: Queue for outgoing responses
        """
        while True:
            try:
                # Get message from incoming queue
                message = await incoming_queue.get()

                # Process with MCP handler
                response = await self.mcp_handler.handle_message(message)

                # Send response if not empty
                if response:
                    event = ServerSentEvent(
                        data=response,
                        event="message"
                    )
                    await outgoing_queue.put(event)

            except asyncio.CancelledError:
                logger.debug("Message processor cancelled")
                break
            except Exception as e:
                logger.error(f"Message processing error: {e}", exc_info=True)

                # Send error event
                error_event = ServerSentEvent(
                    data=json.dumps({
                        "type": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    event="error"
                )
                await outgoing_queue.put(error_event)

    async def _stream_messages(
        self,
        connection_id: str,
        outgoing_queue: asyncio.Queue
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """
        Stream messages from outgoing queue

        Args:
            connection_id: Connection ID
            outgoing_queue: Queue for outgoing messages

        Yields:
            ServerSentEvent objects
        """
        while True:
            try:
                # Get message from queue with timeout
                event = await asyncio.wait_for(
                    outgoing_queue.get(),
                    timeout=self.config.heartbeat_interval * 2
                )

                yield event
                await self.connection_manager.increment_messages(connection_id)

            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except asyncio.CancelledError:
                logger.debug(f"Message streaming cancelled for {connection_id}")
                break
            except Exception as e:
                logger.error(f"Streaming error for {connection_id}: {e}")
                break

    async def send_message_to_connection(
        self,
        connection_id: str,
        message: str
    ) -> bool:
        """
        Send a message to a specific connection

        Args:
            connection_id: Connection ID
            message: MCP message to send

        Returns:
            True if sent successfully, False otherwise
        """
        # This would require storing outgoing queues per connection
        # For now, this is a placeholder
        logger.warning("send_message_to_connection not fully implemented")
        return False

    async def broadcast_message(self, message: str) -> int:
        """
        Broadcast a message to all active connections

        Args:
            message: MCP message to broadcast

        Returns:
            Number of connections that received the message
        """
        # This would require storing outgoing queues per connection
        # For now, this is a placeholder
        logger.warning("broadcast_message not fully implemented")
        return 0
