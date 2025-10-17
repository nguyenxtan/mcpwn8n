"""
Mock API Server - Giả lập 5 APIs của hệ thống ABC
Dùng để demo và testing mà không cần API thật
"""
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="ABC System Mock API",
    description="Mock API server cho demo MCP integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================

class LogQueryRequest(BaseModel):
    timeframe: str = "1h"
    level: Optional[str] = None
    service: Optional[str] = None
    search: Optional[str] = None
    limit: int = 100


# ==================== Mock Data ====================

SERVICES = [
    {
        "service_id": "svc-001",
        "name": "api-gateway",
        "status": "running",
        "version": "2.3.1",
        "endpoints": ["/api/v1/users", "/api/v1/auth"]
    },
    {
        "service_id": "svc-002",
        "name": "user-service",
        "status": "running",
        "version": "1.8.0",
        "endpoints": ["/users", "/profiles"]
    },
    {
        "service_id": "svc-003",
        "name": "payment-service",
        "status": "running",
        "version": "3.2.5",
        "endpoints": ["/payments", "/transactions"]
    },
    {
        "service_id": "svc-004",
        "name": "notification-service",
        "status": "running",
        "version": "1.5.2",
        "endpoints": ["/notifications", "/emails"]
    },
    {
        "service_id": "svc-005",
        "name": "analytics-service",
        "status": "degraded",
        "version": "2.1.0",
        "endpoints": ["/analytics", "/reports"]
    }
]

USERS = [
    {
        "user_id": "usr-001",
        "username": "admin",
        "status": "active",
        "last_login": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
        "session_count": 2
    },
    {
        "user_id": "usr-002",
        "username": "john.doe",
        "status": "active",
        "last_login": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "session_count": 1
    },
    {
        "user_id": "usr-003",
        "username": "jane.smith",
        "status": "active",
        "last_login": (datetime.utcnow() - timedelta(minutes=45)).isoformat(),
        "session_count": 3
    },
    {
        "user_id": "usr-004",
        "username": "bob.wilson",
        "status": "inactive",
        "last_login": (datetime.utcnow() - timedelta(days=5)).isoformat(),
        "session_count": 0
    },
    {
        "user_id": "usr-005",
        "username": "alice.brown",
        "status": "active",
        "last_login": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "session_count": 1
    }
]

LOG_MESSAGES = [
    "User authentication successful",
    "Payment processed successfully",
    "Database connection established",
    "Cache hit for user profile",
    "API request completed in 145ms",
    "Email notification sent",
    "Failed login attempt detected",
    "Rate limit exceeded for IP",
    "Database query timeout",
    "Service health check passed",
    "Backup completed successfully",
    "Invalid token provided",
    "Session expired",
    "File upload completed",
    "Report generation started"
]

LOG_LEVELS = ["debug", "info", "warning", "error"]


# ==================== Helper Functions ====================

def generate_logs(count: int, level_filter: str = None, service_filter: str = None) -> List[Dict[str, Any]]:
    """Generate mock log entries"""
    logs = []
    now = datetime.utcnow()

    for i in range(count):
        level = level_filter if level_filter else random.choice(LOG_LEVELS)
        service = service_filter if service_filter else random.choice(SERVICES)["name"]

        log = {
            "timestamp": (now - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "level": level,
            "service": service,
            "message": random.choice(LOG_MESSAGES),
            "metadata": {
                "request_id": f"req-{random.randint(10000, 99999)}",
                "duration_ms": random.randint(10, 500)
            }
        }
        logs.append(log)

    # Sort by timestamp descending
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return logs


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ABC System Mock API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/system/health",
            "users": "/api/users/status",
            "services": "/api/services/list",
            "logs": "/api/logs/query",
            "metrics": "/api/metrics/current"
        }
    }


@app.get("/api/system/health")
async def get_health():
    """
    API 1: GET /api/system/health - Kiểm tra system health
    """
    # Random có 1 service bị degraded
    services_status = {}
    for svc in SERVICES:
        services_status[svc["name"]] = svc["status"]

    # Overall status
    has_degraded = any(s == "degraded" for s in services_status.values())
    overall_status = "degraded" if has_degraded else "healthy"

    return {
        "status": overall_status,
        "uptime_seconds": random.randint(86400, 2592000),  # 1-30 days
        "timestamp": datetime.utcnow().isoformat(),
        "services": services_status
    }


@app.get("/api/users/status")
async def get_users_status():
    """
    API 2: GET /api/users/status - Lấy user status
    """
    return {
        "users": USERS,
        "total": len(USERS),
        "active": sum(1 for u in USERS if u["status"] == "active"),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/services/list")
async def get_services():
    """
    API 3: GET /api/services/list - Danh sách services
    """
    return {
        "services": SERVICES,
        "total": len(SERVICES),
        "running": sum(1 for s in SERVICES if s["status"] == "running"),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/logs/query")
async def query_logs(request: LogQueryRequest):
    """
    API 4: POST /api/logs/query - Query logs với timeframe
    """
    # Parse timeframe to get count
    timeframe = request.timeframe
    if timeframe.endswith('h'):
        hours = int(timeframe[:-1])
        count = min(hours * 20, request.limit)  # ~20 logs per hour
    elif timeframe.endswith('d'):
        days = int(timeframe[:-1])
        count = min(days * 480, request.limit)  # ~480 logs per day
    elif timeframe.endswith('m'):
        minutes = int(timeframe[:-1])
        count = min(minutes * 2, request.limit)
    else:
        count = 50  # default

    count = min(count, request.limit)

    # Generate logs
    logs = generate_logs(
        count=count,
        level_filter=request.level,
        service_filter=request.service
    )

    # Filter by search if provided
    if request.search:
        logs = [log for log in logs if request.search.lower() in log["message"].lower()]

    return {
        "logs": logs,
        "total": len(logs),
        "timeframe": timeframe,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/metrics/current")
async def get_metrics():
    """
    API 5: GET /api/metrics/current - Metrics hiện tại
    """
    # Generate realistic metrics
    cpu_usage = random.uniform(20, 80)
    memory_usage = random.uniform(40, 85)
    disk_usage = random.uniform(30, 70)

    return {
        "cpu_usage": round(cpu_usage, 2),
        "memory_usage": round(memory_usage, 2),
        "disk_usage": round(disk_usage, 2),
        "network_in_mbps": round(random.uniform(10, 100), 2),
        "network_out_mbps": round(random.uniform(5, 50), 2),
        "request_rate": round(random.uniform(100, 1000), 2),
        "error_rate": round(random.uniform(0.1, 5.0), 2),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check for mock API"""
    return {"status": "healthy", "service": "mock-api"}


# ==================== Middleware for logging ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    print(f"{request.method} {request.url.path} - {response.status_code} - {duration*1000:.2f}ms")

    return response


# ==================== Main ====================

if __name__ == "__main__":
    print("=" * 60)
    print("ABC System Mock API Server")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  - GET  /api/system/health       - System health check")
    print("  - GET  /api/users/status        - User status list")
    print("  - GET  /api/services/list       - Services list")
    print("  - POST /api/logs/query          - Query logs")
    print("  - GET  /api/metrics/current     - Current metrics")
    print("\nStarting server on http://0.0.0.0:8000")
    print("=" * 60)

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
