"""
Async HTTP Client for ABC System APIs
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from models import (
    HealthStatus,
    UserStatus,
    ServiceInfo,
    LogEntry,
    LogQueryParams,
    SystemMetrics,
    SystemCheckResult,
    ABCSystemConfig
)

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, status_code: int, message: str, response: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"API Error {status_code}: {message}")


class ABCSystemClient:
    """
    Async HTTP client for ABC System APIs with retry logic and connection pooling
    """

    def __init__(self, config: ABCSystemConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=config.timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()

        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MCP-SSE-Server-Python/1.0"
        }

        logger.info(f"ABC System Client initialized for {self.base_url}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        async with self._session_lock:
            if self.session is None or self.session.closed:
                connector = aiohttp.TCPConnector(
                    limit=100,  # Connection pool size
                    limit_per_host=30,
                    ttl_dns_cache=300
                )
                self.session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=self.timeout,
                    headers=self.headers
                )
                logger.debug("Created new aiohttp session")

    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.debug("Closed aiohttp session")

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method
            endpoint: API endpoint (relative path)
            **kwargs: Additional arguments for aiohttp request

        Returns:
            Response JSON data

        Raises:
            APIError: If request fails
        """
        await self._ensure_session()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"{method} {url}")

        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_data = await response.json() if response.content_type == 'application/json' else {}

                if response.status >= 400:
                    raise APIError(
                        status_code=response.status,
                        message=f"Request failed: {response.reason}",
                        response=response_data
                    )

                logger.debug(f"{method} {url} -> {response.status}")
                return response_data

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error for {url}: {e}")
            raise
        except asyncio.TimeoutError as e:
            logger.error(f"Request timeout for {url}")
            raise

    # ==================== ABC System API Methods ====================

    async def check_health(self) -> HealthStatus:
        """
        GET /api/system/health - Check system health
        """
        try:
            data = await self._request("GET", "/api/system/health")

            return HealthStatus(
                status=data.get("status", "unknown"),
                timestamp=datetime.utcnow(),
                services=data.get("services", {}),
                uptime_seconds=data.get("uptime_seconds")
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthStatus(
                status="unhealthy",
                timestamp=datetime.utcnow(),
                services={"error": str(e)}
            )

    async def get_user_status(self) -> List[UserStatus]:
        """
        GET /api/users/status - Get user status
        """
        try:
            data = await self._request("GET", "/api/users/status")

            users = data.get("users", [])
            return [
                UserStatus(
                    user_id=user.get("user_id", ""),
                    username=user.get("username", ""),
                    status=user.get("status", "inactive"),
                    last_login=datetime.fromisoformat(user["last_login"]) if user.get("last_login") else None,
                    session_count=user.get("session_count", 0)
                )
                for user in users
            ]
        except Exception as e:
            logger.error(f"Get user status failed: {e}")
            return []

    async def get_services(self) -> List[ServiceInfo]:
        """
        GET /api/services/list - Get services list
        """
        try:
            data = await self._request("GET", "/api/services/list")

            services = data.get("services", [])
            return [
                ServiceInfo(
                    service_id=svc.get("service_id", ""),
                    name=svc.get("name", ""),
                    status=svc.get("status", "unknown"),
                    version=svc.get("version", ""),
                    endpoints=svc.get("endpoints", [])
                )
                for svc in services
            ]
        except Exception as e:
            logger.error(f"Get services failed: {e}")
            return []

    async def query_logs(self, params: Dict[str, Any]) -> List[LogEntry]:
        """
        POST /api/logs/query - Query logs with timeframe
        """
        try:
            # Validate and convert params
            query_params = LogQueryParams(**params)

            data = await self._request(
                "POST",
                "/api/logs/query",
                json=query_params.model_dump()
            )

            logs = data.get("logs", [])
            return [
                LogEntry(
                    timestamp=datetime.fromisoformat(log.get("timestamp", datetime.utcnow().isoformat())),
                    level=log.get("level", "info"),
                    service=log.get("service", "unknown"),
                    message=log.get("message", ""),
                    metadata=log.get("metadata", {})
                )
                for log in logs
            ]
        except Exception as e:
            logger.error(f"Query logs failed: {e}")
            return []

    async def get_metrics(self) -> Optional[SystemMetrics]:
        """
        GET /api/metrics/current - Get current metrics
        """
        try:
            data = await self._request("GET", "/api/metrics/current")

            return SystemMetrics(
                cpu_usage=data.get("cpu_usage", 0.0),
                memory_usage=data.get("memory_usage", 0.0),
                disk_usage=data.get("disk_usage", 0.0),
                network_in_mbps=data.get("network_in_mbps", 0.0),
                network_out_mbps=data.get("network_out_mbps", 0.0),
                request_rate=data.get("request_rate", 0.0),
                error_rate=data.get("error_rate", 0.0),
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Get metrics failed: {e}")
            return None

    # ==================== Composite Methods ====================

    async def check_all_systems(
        self,
        include_health: bool = True,
        include_users: bool = True,
        include_services: bool = True,
        include_logs: bool = True,
        include_metrics: bool = True,
        log_params: Optional[Dict[str, Any]] = None
    ) -> SystemCheckResult:
        """
        Call all 5 APIs in parallel and aggregate results

        Args:
            include_health: Include health check
            include_users: Include user status
            include_services: Include services list
            include_logs: Include log query
            include_metrics: Include metrics
            log_params: Parameters for log query

        Returns:
            SystemCheckResult with all data
        """
        start_time = datetime.utcnow()
        errors = []

        # Build task list based on what's included
        tasks = []
        task_names = []

        if include_health:
            tasks.append(self.check_health())
            task_names.append("health")

        if include_users:
            tasks.append(self.get_user_status())
            task_names.append("users")

        if include_services:
            tasks.append(self.get_services())
            task_names.append("services")

        if include_logs:
            params = log_params or {"timeframe": "1h", "limit": 100}
            tasks.append(self.query_logs(params))
            task_names.append("logs")

        if include_metrics:
            tasks.append(self.get_metrics())
            task_names.append("metrics")

        logger.info(f"Running {len(tasks)} API calls in parallel: {task_names}")

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse results
        result_dict = {}
        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                errors.append(f"{name}: {str(result)}")
                logger.error(f"Task {name} failed: {result}")
                result_dict[name] = None
            else:
                result_dict[name] = result

        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(f"All API calls completed in {execution_time:.2f}ms with {len(errors)} errors")

        return SystemCheckResult(
            health=result_dict.get("health"),
            users=result_dict.get("users"),
            services=result_dict.get("services"),
            logs=result_dict.get("logs"),
            metrics=result_dict.get("metrics"),
            timestamp=datetime.utcnow(),
            execution_time_ms=execution_time,
            errors=errors
        )

    async def selective_check(
        self,
        check_health: bool = False,
        check_users: bool = False,
        check_services: bool = False,
        check_logs: bool = False,
        check_metrics: bool = False,
        log_params: Optional[Dict[str, Any]] = None
    ) -> SystemCheckResult:
        """
        Selectively check specific APIs based on flags

        More flexible version of check_all_systems
        """
        return await self.check_all_systems(
            include_health=check_health,
            include_users=check_users,
            include_services=check_services,
            include_logs=check_logs,
            include_metrics=check_metrics,
            log_params=log_params
        )
