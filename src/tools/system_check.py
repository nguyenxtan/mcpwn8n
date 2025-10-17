"""
System Check Tool - MCP tool for checking ABC system
"""
import logging
from typing import Dict, Any
from datetime import datetime

from models import ToolInputSchema, SystemCheckResult, ABCSystemConfig
from api_client import ABCSystemClient
from tools.nlp_parser import NLPParser

logger = logging.getLogger(__name__)


class SystemCheckTool:
    """
    MCP Tool for checking ABC system with natural language support
    """

    def __init__(self, abc_config: ABCSystemConfig):
        self.name = "check_system_abc"
        self.description = (
            "Kiểm tra toàn bộ hệ thống ABC với 5 API calls song song. "
            "Hỗ trợ ngôn ngữ tự nhiên (Tiếng Việt & English). "
            "Có thể kiểm tra: health status, user status, services, logs, và metrics."
        )

        self.input_schema = ToolInputSchema(
            type="object",
            properties={
                "query": {
                    "type": "string",
                    "description": (
                        "Câu lệnh ngôn ngữ tự nhiên để kiểm tra hệ thống. "
                        "Ví dụ: 'Kiểm tra toàn bộ hệ thống', 'Check all systems', "
                        "'Xem logs 24h gần đây', 'Get current metrics', "
                        "'Kiểm tra user status và services'"
                    )
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters cho các APIs cụ thể",
                    "properties": {
                        "log_timeframe": {
                            "type": "string",
                            "description": "Timeframe cho logs (e.g., '1h', '24h', '7d')"
                        },
                        "log_level": {
                            "type": "string",
                            "enum": ["debug", "info", "warning", "error", "critical"],
                            "description": "Log level filter"
                        },
                        "log_service": {
                            "type": "string",
                            "description": "Filter logs by service name"
                        }
                    }
                }
            },
            required=["query"]
        )

        self.abc_config = abc_config
        self.nlp_parser = NLPParser()

        logger.info("SystemCheckTool initialized")

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the system check tool

        Args:
            params: Tool parameters with 'query' and optional 'filters'

        Returns:
            System check result as dictionary
        """
        query = params.get("query", "")
        filters = params.get("filters", {})

        logger.info(f"Executing system check with query: '{query}'")

        try:
            # Parse natural language query
            intent = self.nlp_parser.parse(query)

            # Override with explicit filters if provided
            if filters:
                if "log_timeframe" in filters:
                    intent.log_timeframe = filters["log_timeframe"]
                if "log_level" in filters:
                    intent.log_level = filters["log_level"]
                if "log_service" in filters:
                    intent.log_service = filters["log_service"]

            # Convert intent to API parameters
            api_params = self.nlp_parser.to_api_params(intent)

            logger.debug(f"API parameters: {api_params}")

            # Execute API calls
            async with ABCSystemClient(self.abc_config) as client:
                result = await client.check_all_systems(**api_params)

            # Convert to dictionary for MCP response
            result_dict = self._format_result(result, intent)

            logger.info(
                f"System check completed: {len(result.errors)} errors, "
                f"{result.execution_time_ms:.2f}ms"
            )

            return result_dict

        except Exception as e:
            logger.error(f"System check failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _format_result(
        self,
        result: SystemCheckResult,
        intent: Any
    ) -> Dict[str, Any]:
        """
        Format SystemCheckResult to dictionary with nice formatting

        Args:
            result: SystemCheckResult object
            intent: ParsedIntent object

        Returns:
            Formatted dictionary
        """
        output = {
            "success": len(result.errors) == 0,
            "timestamp": result.timestamp.isoformat(),
            "execution_time_ms": result.execution_time_ms,
            "query": intent.original_query,
            "confidence": intent.confidence,
        }

        # Add health status if checked
        if result.health:
            output["health"] = {
                "status": result.health.status,
                "uptime_seconds": result.health.uptime_seconds,
                "services": result.health.services
            }

        # Add user status if checked
        if result.users:
            output["users"] = {
                "total": len(result.users),
                "active": sum(1 for u in result.users if u.status == "active"),
                "users": [
                    {
                        "username": u.username,
                        "status": u.status,
                        "session_count": u.session_count,
                        "last_login": u.last_login.isoformat() if u.last_login else None
                    }
                    for u in result.users
                ]
            }

        # Add services if checked
        if result.services:
            output["services"] = {
                "total": len(result.services),
                "running": sum(1 for s in result.services if s.status == "running"),
                "services": [
                    {
                        "name": s.name,
                        "status": s.status,
                        "version": s.version,
                        "endpoints": s.endpoints
                    }
                    for s in result.services
                ]
            }

        # Add logs if checked
        if result.logs:
            output["logs"] = {
                "total": len(result.logs),
                "timeframe": intent.log_timeframe,
                "entries": [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "level": log.level,
                        "service": log.service,
                        "message": log.message,
                        "metadata": log.metadata
                    }
                    for log in result.logs[:50]  # Limit to first 50 for readability
                ]
            }

            # Add log level breakdown
            log_levels = {}
            for log in result.logs:
                log_levels[log.level] = log_levels.get(log.level, 0) + 1
            output["logs"]["level_breakdown"] = log_levels

        # Add metrics if checked
        if result.metrics:
            output["metrics"] = {
                "cpu_usage": result.metrics.cpu_usage,
                "memory_usage": result.metrics.memory_usage,
                "disk_usage": result.metrics.disk_usage,
                "network_in_mbps": result.metrics.network_in_mbps,
                "network_out_mbps": result.metrics.network_out_mbps,
                "request_rate": result.metrics.request_rate,
                "error_rate": result.metrics.error_rate,
                "timestamp": result.metrics.timestamp.isoformat()
            }

        # Add errors if any
        if result.errors:
            output["errors"] = result.errors
            output["success"] = False

        # Add summary
        checks_performed = []
        if result.health:
            checks_performed.append("health")
        if result.users:
            checks_performed.append("users")
        if result.services:
            checks_performed.append("services")
        if result.logs:
            checks_performed.append("logs")
        if result.metrics:
            checks_performed.append("metrics")

        output["summary"] = {
            "checks_performed": checks_performed,
            "total_checks": len(checks_performed),
            "errors_count": len(result.errors)
        }

        return output

    def get_definition(self) -> Dict[str, Any]:
        """Get tool definition for MCP registration"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema.model_dump()
        }
