"""
Pydantic models for MCP protocol and data structures
"""
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class MCPMessageType(str, Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPError(BaseModel):
    """MCP error structure"""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional error data")


class MCPRequest(BaseModel):
    """MCP request message"""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Union[str, int] = Field(..., description="Request ID")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Method parameters")


class MCPResponse(BaseModel):
    """MCP response message"""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Union[str, int] = Field(..., description="Request ID")
    result: Optional[Dict[str, Any]] = Field(None, description="Result data")
    error: Optional[MCPError] = Field(None, description="Error if any")


class MCPNotification(BaseModel):
    """MCP notification message (no response expected)"""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Method parameters")


class ToolInputSchema(BaseModel):
    """Tool input schema definition"""
    type: str = Field("object", description="Schema type")
    properties: Dict[str, Any] = Field(..., description="Input properties")
    required: List[str] = Field(default_factory=list, description="Required fields")


class ToolDefinition(BaseModel):
    """MCP tool definition"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: ToolInputSchema = Field(..., description="Input schema")


class ServerCapabilities(BaseModel):
    """MCP server capabilities"""
    tools: Dict[str, bool] = Field(default_factory=lambda: {"list": True, "call": True})
    resources: Dict[str, bool] = Field(default_factory=dict)
    prompts: Dict[str, bool] = Field(default_factory=dict)
    logging: Dict[str, bool] = Field(default_factory=dict)


class ServerInfo(BaseModel):
    """MCP server information"""
    name: str = Field("mcp-sse-server-python", description="Server name")
    version: str = Field("1.0.0", description="Server version")


class InitializeResult(BaseModel):
    """Initialize method result"""
    protocolVersion: str = Field("2024-11-05", description="MCP protocol version")
    capabilities: ServerCapabilities = Field(default_factory=ServerCapabilities)
    serverInfo: ServerInfo = Field(default_factory=ServerInfo)


# ABC System API Models

class HealthStatus(BaseModel):
    """System health status"""
    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict, description="Individual service status")
    uptime_seconds: Optional[int] = Field(None, description="System uptime")


class UserStatus(BaseModel):
    """User status information"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    status: Literal["active", "inactive", "suspended"] = Field(..., description="User status")
    last_login: Optional[datetime] = Field(None, description="Last login time")
    session_count: int = Field(0, description="Active sessions")


class ServiceInfo(BaseModel):
    """Service information"""
    service_id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    status: Literal["running", "stopped", "error"] = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    endpoints: List[str] = Field(default_factory=list, description="Service endpoints")


class LogQueryParams(BaseModel):
    """Log query parameters"""
    timeframe: str = Field("1h", description="Timeframe (e.g., 1h, 24h, 7d)")
    level: Optional[Literal["debug", "info", "warning", "error", "critical"]] = Field(None)
    service: Optional[str] = Field(None, description="Filter by service")
    search: Optional[str] = Field(None, description="Search query")
    limit: int = Field(100, ge=1, le=10000, description="Result limit")


class LogEntry(BaseModel):
    """Log entry"""
    timestamp: datetime = Field(..., description="Log timestamp")
    level: str = Field(..., description="Log level")
    service: str = Field(..., description="Service name")
    message: str = Field(..., description="Log message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MetricValue(BaseModel):
    """Metric value"""
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = Field(default_factory=dict, description="Metric labels")


class SystemMetrics(BaseModel):
    """Current system metrics"""
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    network_in_mbps: float = Field(..., ge=0, description="Network inbound Mbps")
    network_out_mbps: float = Field(..., ge=0, description="Network outbound Mbps")
    request_rate: float = Field(..., ge=0, description="Requests per second")
    error_rate: float = Field(..., ge=0, le=100, description="Error rate percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemCheckResult(BaseModel):
    """Complete system check result"""
    health: Optional[HealthStatus] = Field(None, description="Health check result")
    users: Optional[List[UserStatus]] = Field(None, description="User status list")
    services: Optional[List[ServiceInfo]] = Field(None, description="Services list")
    logs: Optional[List[LogEntry]] = Field(None, description="Recent logs")
    metrics: Optional[SystemMetrics] = Field(None, description="Current metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")


# n8n Integration Models

class N8NWebhookRequest(BaseModel):
    """Request from n8n webhook"""
    tool: str = Field("check_system_abc", description="Tool to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    webhook_id: str = Field(..., description="Webhook ID")
    execution_id: Optional[str] = Field(None, description="n8n execution ID")


class N8NWebhookResponse(BaseModel):
    """Response to n8n webhook"""
    success: bool = Field(..., description="Execution success")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data")
    tool: str = Field(..., description="Tool executed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = Field(None, description="Execution time")
    error: Optional[str] = Field(None, description="Error message if failed")


# SSE Models

class SSEEvent(BaseModel):
    """SSE event structure"""
    event: str = Field(..., description="Event type")
    data: str = Field(..., description="Event data (JSON string)")
    id: Optional[str] = Field(None, description="Event ID")
    retry: Optional[int] = Field(None, description="Retry timeout in ms")


# Configuration Models

class ServerConfig(BaseModel):
    """Server configuration"""
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(3001, ge=1, le=65535, description="Server port")
    workers: int = Field(4, ge=1, description="Number of workers")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO")


class ABCSystemConfig(BaseModel):
    """ABC System API configuration"""
    base_url: str = Field(..., description="Base URL")
    api_key: str = Field(..., description="API key")
    timeout: int = Field(30, ge=1, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, description="Max retry attempts")
    retry_backoff: float = Field(1.0, ge=0, description="Retry backoff multiplier")


class N8NConfig(BaseModel):
    """n8n configuration"""
    instance_url: str = Field(..., description="n8n instance URL")
    api_key: Optional[str] = Field(None, description="n8n API key")
    webhook_path: str = Field("mcp-system-check", description="Webhook path")


class SSEConfig(BaseModel):
    """SSE configuration"""
    heartbeat_interval: int = Field(30, ge=1, description="Heartbeat interval in seconds")
    reconnect_timeout: int = Field(5, ge=1, description="Reconnect timeout in seconds")
    max_connections: int = Field(100, ge=1, description="Max concurrent connections")


class AppConfig(BaseModel):
    """Complete application configuration"""
    server: ServerConfig = Field(default_factory=ServerConfig)
    abc_system: ABCSystemConfig
    n8n: N8NConfig
    sse: SSEConfig = Field(default_factory=SSEConfig)
