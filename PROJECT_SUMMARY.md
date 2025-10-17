# 📦 MCP SSE Server Python - Project Summary

## Tổng quan dự án

Đây là một **production-ready MCP (Model Context Protocol) Server** viết bằng Python với SSE transport, tích hợp sẵn:
- ✅ 5 APIs của hệ thống ABC (có Mock API để demo)
- ✅ n8n webhook integration
- ✅ Natural Language processing (Tiếng Việt + English)
- ✅ Full monitoring stack (Prometheus + Grafana)

---

## 📁 Cấu trúc project

```
mcp-sse-server-python/
├── src/                          # Source code
│   ├── main.py                   # FastAPI app - Entry point
│   ├── models.py                 # Pydantic models
│   ├── mcp_protocol.py           # MCP protocol handler
│   ├── sse_handler.py            # SSE connection manager
│   ├── api_client.py             # Async HTTP client
│   ├── n8n_integration.py        # n8n webhook handler
│   └── tools/
│       ├── nlp_parser.py         # NLP parser (VI/EN)
│       └── system_check.py       # System check tool
│
├── mock-api/                     # Mock API cho demo
│   ├── server.py                 # Mock API server
│   ├── requirements.txt
│   └── Dockerfile
│
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Production Dockerfile
├── docker-compose.yml            # Production compose
├── docker-compose.dev.yml        # Development compose (with Mock API)
├── prometheus.yml                # Prometheus config
│
├── .env.example                  # Production env template
├── .env.dev                      # Development env
├── .gitignore
│
├── demo-start.sh                 # Quick start script ⭐
├── test-demo.sh                  # Automated tests ⭐
│
├── README.md                     # Full documentation
├── DEMO.md                       # Demo guide ⭐
├── QUICKSTART.md                 # Quick start guide ⭐
└── PROJECT_SUMMARY.md            # This file
```

---

## 🎯 Core Components

### 1. MCP Protocol Handler (`mcp_protocol.py`)
- JSON-RPC 2.0 implementation
- Tool registration & execution
- Request/response handling
- Error handling với proper error codes

### 2. SSE Handler (`sse_handler.py`)
- Server-Sent Events transport
- Connection management
- Heartbeat mechanism (30s interval)
- Concurrent connection support (100 max)

### 3. API Client (`api_client.py`)
- Async HTTP client với aiohttp
- Connection pooling
- Retry logic với tenacity (3 retries)
- Parallel execution của 5 APIs với asyncio.gather()

### 4. Natural Language Parser (`nlp_parser.py`)
- Regex-based pattern matching
- Supports Tiếng Việt và English
- Intent detection cho 5 loại checks:
  - health, users, services, logs, metrics
- Timeframe parsing (1h, 24h, 7d, etc.)

### 5. System Check Tool (`system_check.py`)
- MCP tool implementation
- Natural language query processing
- API orchestration
- Result formatting

### 6. n8n Integration (`n8n_integration.py`)
- Webhook endpoints
- Tool execution từ n8n
- Response formatting cho n8n workflows

---

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Python 3.11** - Latest stable Python
- **aiohttp** - Async HTTP client
- **sse-starlette** - SSE support
- **Pydantic** - Data validation
- **structlog** - Structured logging

### Monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **prometheus-client** - Python Prometheus integration

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **uvicorn** - ASGI server

---

## 📊 APIs Implementation

### 5 ABC System APIs

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/api/system/health` | GET | System health status |
| 2 | `/api/users/status` | GET | User status list |
| 3 | `/api/services/list` | GET | Services list |
| 4 | `/api/logs/query` | POST | Query logs với filters |
| 5 | `/api/metrics/current` | GET | Current system metrics |

Tất cả đều có **Mock implementation** trong `mock-api/server.py`

---

## 🚀 Deployment Options

### 1. Development (với Mock API)
```bash
./demo-start.sh
```
Chạy: Mock API + MCP Server + Prometheus + Grafana

### 2. Production (với real APIs)
```bash
docker-compose up -d
```
Chỉ cần set `.env` với real API credentials

### 3. Kubernetes
Ready cho K8s deployment:
- Health checks: `/health/live`, `/health/ready`
- Graceful shutdown
- Environment-based configuration
- Prometheus metrics

---

## 📈 Monitoring & Metrics

### Prometheus Metrics Exposed

```
mcp_requests_total              # Total requests
mcp_request_duration_seconds    # Request duration
mcp_sse_connections_active      # Active SSE connections
mcp_tool_executions_total       # Tool executions
```

### Grafana Dashboards

Login: `admin/admin` tại http://localhost:3000

Create dashboards với queries:
```promql
rate(mcp_requests_total[5m])
mcp_sse_connections_active
histogram_quantile(0.95, mcp_request_duration_seconds)
```

---

## 🧪 Testing

### Automated Tests
```bash
./test-demo.sh
```

Tests cover:
- ✅ Mock API endpoints (5 APIs)
- ✅ MCP Server endpoints (health, info, tools)
- ✅ n8n webhooks (Vietnamese & English)
- ✅ Natural Language parsing
- ✅ System integration

### Manual Testing

Xem [DEMO.md](DEMO.md) cho:
- SSE connection testing
- MCP protocol testing
- Natural language queries
- n8n webhook testing

---

## 🌍 Natural Language Support

### Supported Languages
- 🇻🇳 Tiếng Việt
- 🇬🇧 English

### Example Queries

**Vietnamese:**
```
"Kiểm tra toàn bộ hệ thống"
"Xem logs 24h gần đây"
"Tìm lỗi trong logs 1 giờ qua"
"Lấy metrics hiện tại"
```

**English:**
```
"Check all systems"
"Get logs from last 24 hours"
"Search for errors in recent logs"
"Get current system metrics"
```

Parser tự động detect intent và gọi đúng APIs.

---

## 🔐 Security Features

- ✅ API key authentication
- ✅ CORS configuration
- ✅ Input validation với Pydantic
- ✅ Rate limiting ready
- ✅ Non-root Docker user
- ✅ Environment-based secrets

**Production recommendations:**
- Configure CORS properly
- Add rate limiting
- Use HTTPS (nginx/traefik)
- Implement authentication middleware
- Use secrets management (Vault, K8s secrets)

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 5-minute setup guide ⭐ |
| **DEMO.md** | Comprehensive demo guide |
| **README.md** | Full technical documentation |
| **PROJECT_SUMMARY.md** | This overview |

**Start here:** [QUICKSTART.md](QUICKSTART.md) → [DEMO.md](DEMO.md) → [README.md](README.md)

---

## 🎓 Learning Path

### For Beginners
1. Run `./demo-start.sh`
2. Read [QUICKSTART.md](QUICKSTART.md)
3. Try example commands
4. Explore [DEMO.md](DEMO.md)

### For Developers
1. Read [README.md](README.md)
2. Explore source code in `src/`
3. Understand MCP protocol
4. Customize tools in `src/tools/`

### For DevOps
1. Review Docker setup
2. Check monitoring configuration
3. Read production deployment section
4. Plan K8s deployment

---

## 🛠️ Customization Guide

### Add New Tool

1. Create `src/tools/my_tool.py`:
```python
class MyTool:
    def __init__(self):
        self.name = "my_tool"
        self.description = "..."
        self.input_schema = {...}

    async def execute(self, params):
        # Your logic here
        return result
```

2. Register in `src/main.py`:
```python
my_tool = MyTool()
mcp_handler.register_tool(
    name=my_tool.name,
    description=my_tool.description,
    input_schema=my_tool.input_schema,
    handler=my_tool.execute
)
```

### Add New API Endpoint

Edit `src/api_client.py`:
```python
async def my_new_api(self):
    data = await self._request("GET", "/api/my-endpoint")
    return data
```

### Customize NLP Patterns

Edit `src/tools/nlp_parser.py`:
```python
self.patterns = {
    "my_intent": [
        r"pattern1",
        r"pattern2",
    ]
}
```

---

## 📊 Performance Characteristics

### Throughput
- **Concurrent API calls:** 5 APIs in parallel
- **Connection pooling:** Up to 100 connections
- **Worker processes:** 4 (configurable)
- **SSE connections:** 100 max (configurable)

### Latency
- **Health check:** <10ms
- **System check (all 5 APIs):** ~100-300ms (with mocks)
- **SSE heartbeat:** Every 30s
- **Retry timeout:** Exponential backoff (1s, 2s, 4s)

### Scalability
- Horizontal scaling ready
- Stateless design
- Connection pooling
- Async I/O throughout

---

## 🎯 Use Cases

### 1. System Monitoring
Monitor multiple systems via natural language queries from n8n workflows.

### 2. Operations Automation
Automate system checks, log analysis, and alerting with n8n.

### 3. ChatOps Integration
Integrate with Slack/Teams via n8n để control systems with natural language.

### 4. API Aggregation
Aggregate multiple APIs into single natural language interface.

### 5. Development Tool
Use MCP protocol để integrate with AI tools (Claude, etc.).

---

## 🚦 Project Status

- ✅ **Core Features:** Complete
- ✅ **Mock API:** Complete
- ✅ **Documentation:** Complete
- ✅ **Testing:** Automated tests ready
- ✅ **Monitoring:** Prometheus + Grafana ready
- ✅ **Docker:** Multi-stage build ready
- 🟡 **Production deployment:** Needs real API credentials
- 🟡 **n8n workflows:** Sample workflows needed
- 🟡 **Authentication:** Basic (needs enhancement for production)

---

## 🎉 Quick Win

Muốn thấy kết quả ngay? 3 lệnh:

```bash
cd mcp-sse-server-python
./demo-start.sh
./test-demo.sh
```

Done! Bạn có một working MCP server với monitoring đầy đủ.

---

## 📞 Support & Resources

- **Documentation:** See README.md, DEMO.md, QUICKSTART.md
- **Issues:** GitHub Issues
- **MCP Spec:** https://modelcontextprotocol.io
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **n8n Docs:** https://docs.n8n.io

---

**Built with ❤️ using Python, FastAPI, and modern async patterns**
