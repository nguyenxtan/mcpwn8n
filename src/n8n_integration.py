"""
n8n Integration Module
Handles webhook requests from n8n and integrates with MCP tools
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import aiohttp
from fastapi import HTTPException

from models import (
    N8NWebhookRequest,
    N8NWebhookResponse,
    N8NConfig,
    ABCSystemConfig
)
from tools.system_check import SystemCheckTool

logger = logging.getLogger(__name__)


class N8NIntegration:
    """
    Handles integration with n8n workflows
    """

    def __init__(self, n8n_config: N8NConfig, abc_config: ABCSystemConfig):
        self.config = n8n_config
        self.n8n_url = n8n_config.instance_url
        self.api_key = n8n_config.api_key

        # Initialize tools
        self.tools = {
            "check_system_abc": SystemCheckTool(abc_config)
        }

        logger.info(f"n8n Integration initialized for {self.n8n_url}")

    async def handle_webhook_request(
        self,
        webhook_id: str,
        request_data: Dict[str, Any]
    ) -> N8NWebhookResponse:
        """
        Handle incoming webhook request from n8n

        Args:
            webhook_id: Webhook identifier
            request_data: Request payload from n8n

        Returns:
            N8NWebhookResponse with execution result
        """
        start_time = datetime.utcnow()

        try:
            # Parse request
            webhook_request = N8NWebhookRequest(
                tool=request_data.get("tool", "check_system_abc"),
                params=request_data.get("params", {}),
                webhook_id=webhook_id,
                execution_id=request_data.get("executionId")
            )

            logger.info(
                f"Processing n8n webhook: {webhook_id} "
                f"(tool: {webhook_request.tool}, execution: {webhook_request.execution_id})"
            )

            # Execute tool
            result = await self._execute_tool(
                webhook_request.tool,
                webhook_request.params
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Build response
            response = N8NWebhookResponse(
                success=True,
                data=result,
                tool=webhook_request.tool,
                timestamp=datetime.utcnow(),
                execution_time_ms=execution_time
            )

            logger.info(
                f"Webhook {webhook_id} completed successfully in {execution_time:.2f}ms"
            )

            return response

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.error(
                f"Webhook {webhook_id} failed after {execution_time:.2f}ms: {e}",
                exc_info=True
            )

            return N8NWebhookResponse(
                success=False,
                data=None,
                tool=request_data.get("tool", "unknown"),
                timestamp=datetime.utcnow(),
                execution_time_ms=execution_time,
                error=str(e)
            )

    async def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name

        Args:
            tool_name: Name of the tool to execute
            params: Tool parameters

        Returns:
            Tool execution result

        Raises:
            HTTPException: If tool not found
        """
        if tool_name not in self.tools:
            raise HTTPException(
                status_code=400,
                detail=f"Tool not found: {tool_name}"
            )

        tool = self.tools[tool_name]
        result = await tool.execute(params)

        return result

    async def trigger_workflow(
        self,
        webhook_path: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger an n8n workflow via webhook

        Args:
            webhook_path: Webhook path (e.g., 'mcp-system-check')
            data: Data to send to workflow

        Returns:
            n8n workflow response

        Raises:
            Exception: If workflow trigger fails
        """
        url = f"https://{self.n8n_url}/webhook/{webhook_path}"

        logger.info(f"Triggering n8n workflow: {url}")

        try:
            headers = {
                "Content-Type": "application/json"
            }

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(
                            f"n8n workflow trigger failed: {response.status} - {error_text}"
                        )

                    result = await response.json()
                    logger.info(f"n8n workflow triggered successfully: {webhook_path}")
                    return result

        except aiohttp.ClientError as e:
            logger.error(f"Failed to trigger n8n workflow: {e}")
            raise Exception(f"n8n workflow trigger error: {str(e)}")

    async def create_webhook(self, workflow_id: str) -> str:
        """
        Create a webhook in n8n (requires n8n API access)

        Args:
            workflow_id: n8n workflow ID

        Returns:
            Webhook URL

        Note:
            This requires n8n API access and is currently a placeholder
        """
        if not self.api_key:
            raise Exception("n8n API key required for webhook creation")

        # This would use the n8n API to create a webhook
        # For now, return a placeholder
        webhook_path = f"webhook-{workflow_id}"

        logger.warning("create_webhook is a placeholder implementation")

        return f"https://{self.n8n_url}/webhook/{webhook_path}"

    async def get_workflow_executions(
        self,
        workflow_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent executions for a workflow (requires n8n API access)

        Args:
            workflow_id: n8n workflow ID
            limit: Maximum number of executions to return

        Returns:
            List of workflow executions

        Note:
            This requires n8n API access and is currently a placeholder
        """
        if not self.api_key:
            raise Exception("n8n API key required for execution history")

        # This would use the n8n API to get executions
        # For now, return empty list
        logger.warning("get_workflow_executions is a placeholder implementation")

        return []

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools for n8n integration

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": name,
                "description": tool.description,
                "input_schema": tool.input_schema.model_dump()
            }
            for name, tool in self.tools.items()
        ]

    async def validate_webhook(self, webhook_id: str) -> bool:
        """
        Validate if a webhook ID is valid

        Args:
            webhook_id: Webhook ID to validate

        Returns:
            True if valid, False otherwise
        """
        # Simple validation - check if webhook_id matches expected pattern
        # In production, this should check against a database or n8n API
        if not webhook_id or len(webhook_id) < 3:
            return False

        return True

    async def send_notification(
        self,
        webhook_path: str,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification to n8n workflow

        Args:
            webhook_path: Webhook path for notifications
            notification_type: Type of notification (e.g., 'alert', 'info', 'error')
            message: Notification message
            data: Additional data

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            payload = {
                "type": notification_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data or {}
            }

            await self.trigger_workflow(webhook_path, payload)
            logger.info(f"Notification sent: {notification_type} - {message}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
