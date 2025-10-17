"""
MCP Protocol Handler - Core implementation of Model Context Protocol
"""
import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime

from models import (
    MCPRequest,
    MCPResponse,
    MCPNotification,
    MCPError,
    ToolDefinition,
    InitializeResult,
    ServerCapabilities,
    ServerInfo
)

logger = logging.getLogger(__name__)


class MCPProtocolHandler:
    """
    Handles MCP protocol message processing and tool management
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
        self.client_info: Optional[Dict[str, Any]] = None
        self.session_id = str(uuid.uuid4())

        logger.info(f"MCP Protocol Handler initialized with session: {self.session_id}")

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> None:
        """
        Register a tool with the MCP server

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for tool input
            handler: Async function to execute the tool
        """
        self.tools[name] = {
            "definition": ToolDefinition(
                name=name,
                description=description,
                inputSchema=input_schema
            ),
            "handler": handler
        }
        logger.info(f"Registered tool: {name}")

    async def handle_message(self, message_str: str) -> str:
        """
        Process incoming MCP message and return response

        Args:
            message_str: JSON-RPC message string

        Returns:
            JSON-RPC response string
        """
        try:
            message = json.loads(message_str)

            # Validate JSON-RPC version
            if message.get("jsonrpc") != "2.0":
                return self._error_response(
                    message.get("id"),
                    -32600,
                    "Invalid JSON-RPC version"
                )

            # Check if it's a request or notification
            if "id" in message:
                # Request - needs response
                return await self._handle_request(message)
            else:
                # Notification - no response needed
                await self._handle_notification(message)
                return ""

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return self._error_response(None, -32700, "Parse error")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return self._error_response(None, -32603, f"Internal error: {str(e)}")

    async def _handle_request(self, message: Dict[str, Any]) -> str:
        """Handle JSON-RPC request"""
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        logger.debug(f"Handling request: {method} (id: {request_id})")

        try:
            # Route to appropriate handler
            if method == "initialize":
                result = await self._handle_initialize(params)
            elif method == "initialized":
                # Client confirmation of initialization
                return ""
            elif method == "tools/list":
                result = await self._handle_tools_list(params)
            elif method == "tools/call":
                result = await self._handle_tools_call(params)
            elif method == "ping":
                result = {"status": "pong", "timestamp": datetime.utcnow().isoformat()}
            else:
                return self._error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )

            # Build success response
            response = MCPResponse(
                id=request_id,
                result=result
            )
            return response.model_dump_json()

        except Exception as e:
            logger.error(f"Error executing method {method}: {e}", exc_info=True)
            return self._error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )

    async def _handle_notification(self, message: Dict[str, Any]) -> None:
        """Handle JSON-RPC notification (no response)"""
        method = message.get("method")
        params = message.get("params", {})

        logger.debug(f"Handling notification: {method}")

        if method == "notifications/cancelled":
            # Handle cancellation
            operation_id = params.get("id")
            logger.info(f"Operation cancelled: {operation_id}")
        elif method == "notifications/progress":
            # Handle progress update
            logger.debug(f"Progress update: {params}")

    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle initialize request

        Returns server capabilities and info
        """
        self.client_info = params
        self.initialized = True

        logger.info(f"Client initialized: {params.get('clientInfo', {})}")

        result = InitializeResult(
            protocolVersion="2024-11-05",
            capabilities=ServerCapabilities(
                tools={"list": True, "call": True},
                resources={},
                prompts={},
                logging={}
            ),
            serverInfo=ServerInfo(
                name="mcp-sse-server-python",
                version="1.0.0"
            )
        )

        return result.model_dump()

    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/list request

        Returns list of available tools
        """
        if not self.initialized:
            raise Exception("Server not initialized")

        tools_list = [
            tool["definition"].model_dump()
            for tool in self.tools.values()
        ]

        logger.debug(f"Listing {len(tools_list)} tools")

        return {
            "tools": tools_list
        }

    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request

        Executes the requested tool and returns result
        """
        if not self.initialized:
            raise Exception("Server not initialized")

        tool_name = params.get("name")
        tool_params = params.get("arguments", {})

        if tool_name not in self.tools:
            raise Exception(f"Tool not found: {tool_name}")

        logger.info(f"Calling tool: {tool_name}")

        # Execute tool handler
        tool = self.tools[tool_name]
        start_time = datetime.utcnow()

        try:
            result = await tool["handler"](tool_params)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.info(f"Tool {tool_name} completed in {execution_time:.2f}ms")

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ],
                "isError": False
            }

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(f"Tool {tool_name} failed after {execution_time:.2f}ms: {e}", exc_info=True)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }

    def _error_response(
        self,
        request_id: Optional[Any],
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build JSON-RPC error response

        Args:
            request_id: Request ID (can be None)
            code: Error code
            message: Error message
            data: Additional error data

        Returns:
            JSON-RPC error response string
        """
        error = MCPError(code=code, message=message, data=data)
        response = MCPResponse(
            id=request_id if request_id is not None else 0,
            error=error
        )
        return response.model_dump_json()

    def create_notification(self, method: str, params: Dict[str, Any]) -> str:
        """
        Create a notification message (server to client)

        Args:
            method: Notification method name
            params: Notification parameters

        Returns:
            JSON-RPC notification string
        """
        notification = MCPNotification(
            method=method,
            params=params
        )
        return notification.model_dump_json()

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of registered tools"""
        return [
            tool["definition"].model_dump()
            for tool in self.tools.values()
        ]

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "mcp-sse-server-python",
            "version": "1.0.0",
            "session_id": self.session_id,
            "initialized": self.initialized,
            "tools_count": len(self.tools),
            "client_info": self.client_info
        }
