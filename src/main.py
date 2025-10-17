"""
FastAPI Main Application
MCP Server with SSE support and n8n integration
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
from dotenv import load_dotenv

from models import (
    AppConfig,
    ServerConfig,
    ABCSystemConfig,
    N8NConfig,
    SSEConfig,
    N8NWebhookRequest
)
from mcp_protocol import MCPProtocolHandler
from sse_handler import SSEHandler, SSEConnectionManager
from n8n_integration import N8NIntegration
from tools.system_check import SystemCheckTool

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'mcp_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'mcp_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)
ACTIVE_SSE_CONNECTIONS = Gauge(
    'mcp_sse_connections_active',
    'Number of active SSE connections'
)
TOOL_EXECUTIONS = Counter(
    'mcp_tool_executions_total',
    'Total number of tool executions',
    ['tool_name', 'status']
)

# Global instances
mcp_handler: MCPProtocolHandler
sse_manager: SSEConnectionManager
sse_handler: SSEHandler
n8n_integration: N8NIntegration
app_config: AppConfig


def load_config() -> AppConfig:
    """Load configuration from environment variables"""
    return AppConfig(
        server=ServerConfig(
            host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_SERVER_PORT", "3001")),
            workers=int(os.getenv("MCP_SERVER_WORKERS", "4")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        ),
        abc_system=ABCSystemConfig(
            base_url=os.getenv("ABC_SYSTEM_BASE_URL", "https://api.abc.com"),
            api_key=os.getenv("ABC_API_KEY", ""),
            timeout=int(os.getenv("ABC_TIMEOUT", "30")),
            max_retries=int(os.getenv("ABC_MAX_RETRIES", "3")),
            retry_backoff=float(os.getenv("ABC_RETRY_BACKOFF", "1.0"))
        ),
        n8n=N8NConfig(
            instance_url=os.getenv("N8N_INSTANCE_URL", "n8n-prod.iconiclogs.com"),
            api_key=os.getenv("N8N_API_KEY"),
            webhook_path=os.getenv("N8N_WEBHOOK_PATH", "mcp-system-check")
        ),
        sse=SSEConfig(
            heartbeat_interval=int(os.getenv("SSE_HEARTBEAT_INTERVAL", "30")),
            reconnect_timeout=int(os.getenv("SSE_RECONNECT_TIMEOUT", "5")),
            max_connections=int(os.getenv("SSE_MAX_CONNECTIONS", "100"))
        )
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global mcp_handler, sse_manager, sse_handler, n8n_integration, app_config

    logger.info("Starting MCP SSE Server...")

    # Load configuration
    app_config = load_config()

    # Initialize MCP protocol handler
    mcp_handler = MCPProtocolHandler()

    # Initialize SSE connection manager
    sse_manager = SSEConnectionManager(app_config.sse)

    # Initialize SSE handler
    sse_handler = SSEHandler(mcp_handler, sse_manager, app_config.sse)

    # Initialize n8n integration
    n8n_integration = N8NIntegration(app_config.n8n, app_config.abc_system)

    # Register tools
    system_check_tool = SystemCheckTool(app_config.abc_system)
    mcp_handler.register_tool(
        name=system_check_tool.name,
        description=system_check_tool.description,
        input_schema=system_check_tool.input_schema.model_dump(),
        handler=system_check_tool.execute
    )

    logger.info(
        "MCP SSE Server started",
        port=app_config.server.port,
        tools=len(mcp_handler.tools),
        n8n_instance=app_config.n8n.instance_url
    )

    yield

    # Cleanup
    logger.info("Shutting down MCP SSE Server...")


# Create FastAPI app
app = FastAPI(
    title="MCP SSE Server",
    description="Model Context Protocol Server with SSE transport and n8n integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request metrics"""
    method = request.method
    endpoint = request.url.path

    with REQUEST_DURATION.labels(method=method, endpoint=endpoint).time():
        response = await call_next(request)

    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    return response


# ==================== SSE Endpoints ====================

@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    SSE endpoint for MCP protocol communication

    Clients connect to this endpoint to establish SSE connection
    and communicate with MCP protocol
    """
    connection_id = request.query_params.get("connection_id")

    logger.info("New SSE connection request", connection_id=connection_id)

    ACTIVE_SSE_CONNECTIONS.inc()

    try:
        return EventSourceResponse(
            sse_handler.handle_sse_connection(connection_id),
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
    finally:
        ACTIVE_SSE_CONNECTIONS.dec()


# ==================== n8n Webhook Endpoints ====================

@app.post("/n8n/webhook/{webhook_id}")
async def n8n_webhook(webhook_id: str, request: Request):
    """
    n8n webhook endpoint

    Receives requests from n8n workflows and executes MCP tools
    """
    try:
        # Validate webhook
        if not await n8n_integration.validate_webhook(webhook_id):
            raise HTTPException(status_code=400, detail="Invalid webhook ID")

        # Parse request body
        request_data = await request.json()

        logger.info(
            "n8n webhook request",
            webhook_id=webhook_id,
            tool=request_data.get("tool")
        )

        # Handle webhook
        response = await n8n_integration.handle_webhook_request(
            webhook_id,
            request_data
        )

        # Record metrics
        status = "success" if response.success else "error"
        TOOL_EXECUTIONS.labels(
            tool_name=response.tool,
            status=status
        ).inc()

        return JSONResponse(content=response.model_dump())

    except Exception as e:
        logger.error("Webhook error", webhook_id=webhook_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/n8n/tools")
async def list_n8n_tools():
    """
    List available tools for n8n integration
    """
    tools = n8n_integration.get_available_tools()
    return JSONResponse(content={"tools": tools})


# ==================== Health & Monitoring Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "server": "mcp-sse-server-python",
        "version": "1.0.0",
        "active_connections": len(sse_manager.get_all_connections()),
        "registered_tools": len(mcp_handler.tools)
    })


@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe"""
    return JSONResponse(content={"status": "alive"})


@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe"""
    # Check if server is ready to accept connections
    ready = mcp_handler is not None and sse_manager is not None

    if not ready:
        raise HTTPException(status_code=503, detail="Not ready")

    return JSONResponse(content={"status": "ready"})


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ==================== Info Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return JSONResponse(content={
        "name": "MCP SSE Server",
        "version": "1.0.0",
        "description": "Model Context Protocol Server with SSE transport",
        "endpoints": {
            "sse": "/sse",
            "n8n_webhook": "/n8n/webhook/{webhook_id}",
            "n8n_tools": "/n8n/tools",
            "health": "/health",
            "metrics": "/metrics",
            "info": "/info"
        }
    })


@app.get("/info")
async def server_info():
    """Detailed server information"""
    return JSONResponse(content={
        "server": mcp_handler.get_server_info(),
        "connections": {
            "active": len(sse_manager.get_all_connections()),
            "max": app_config.sse.max_connections,
            "details": sse_manager.get_all_connections()
        },
        "tools": mcp_handler.get_tool_list(),
        "config": {
            "sse_heartbeat_interval": app_config.sse.heartbeat_interval,
            "n8n_instance": app_config.n8n.instance_url,
            "abc_system_url": app_config.abc_system.base_url
        }
    })


# ==================== Admin Endpoints ====================

@app.get("/connections")
async def list_connections():
    """List all active SSE connections"""
    connections = sse_manager.get_all_connections()
    return JSONResponse(content={
        "total": len(connections),
        "connections": connections
    })


@app.get("/tools")
async def list_tools():
    """List all registered MCP tools"""
    tools = mcp_handler.get_tool_list()
    return JSONResponse(content={"tools": tools})


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ==================== Main Entry Point ====================

if __name__ == "__main__":
    import uvicorn

    config = load_config()

    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
        log_level=config.server.log_level.lower(),
        reload=False  # Set to True for development
    )
