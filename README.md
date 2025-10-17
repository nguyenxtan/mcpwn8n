# MCP SSE Server Python

Model Context Protocol (MCP) Server với SSE transport được viết bằng Python, tích hợp với n8n instance tại `n8n-prod.iconiclogs.com`.

## Tính năng

- **MCP Protocol Implementation**: Triển khai đầy đủ MCP protocol với JSON-RPC 2.0
- **SSE Transport**: Server-Sent Events để real-time communication
- **n8n Integration**: Webhook endpoints để tích hợp với n8n workflows
- **Natural Language Support**: Hỗ trợ Tiếng Việt và English cho queries
- **Async API Calls**: Gọi 5 APIs của hệ thống ABC song song với asyncio
- **Health Monitoring**: Health check và Prometheus metrics
- **Production Ready**: Docker support, graceful shutdown, comprehensive logging

## Kiến trúc

```
mcp-sse-server-python/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── mcp_protocol.py         # MCP protocol handler
│   ├── sse_handler.py          # SSE connection manager
│   ├── api_client.py           # Async HTTP client cho ABC system
│   ├── n8n_integration.py      # n8n webhook handler
│   └── tools/
│       ├── nlp_parser.py       # Natural language parser
│       └── system_check.py     # System check tool
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 5 APIs của Hệ thống ABC

1. **GET /api/system/health** - Kiểm tra system health
2. **GET /api/users/status** - Lấy user status
3. **GET /api/services/list** - Danh sách services
4. **POST /api/logs/query** - Query logs với timeframe
5. **GET /api/metrics/current** - Metrics hiện tại

## Cài đặt

> **🚀 DEMO MODE**: Không có API thật? Xem [DEMO.md](DEMO.md) để chạy ngay với Mock API!

### Yêu cầu

- Python 3.11+
- Docker & Docker Compose (optional)
- n8n instance tại `n8n-prod.iconiclogs.com` (optional cho demo)
- API key cho ABC System (hoặc dùng Mock API)

### 1. Clone và Setup

```bash
cd mcp-sse-server-python

# Copy .env.example thành .env
cp .env.example .env

# Chỉnh sửa .env với thông tin thực tế
nano .env
```

### 2. Cấu hình .env

```bash
# ABC System Configuration
ABC_SYSTEM_BASE_URL=https://api.abc.com
ABC_API_KEY=your_actual_api_key_here

# n8n Integration
N8N_INSTANCE_URL=n8n-prod.iconiclogs.com
N8N_API_KEY=your_n8n_api_key_here
N8N_WEBHOOK_PATH=mcp-system-check
```

### 3. Installation Options

#### Option A: Local Python

```bash
# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python src/main.py
```

#### Option B: Docker

```bash
# Build và run với Docker Compose
docker-compose up -d

# Xem logs
docker-compose logs -f mcp-server

# Stop
docker-compose down
```

#### Option C: Docker only (không compose)

```bash
# Build image
docker build -t mcp-sse-server .

# Run container
docker run -d \
  -p 3001:3001 \
  --name mcp-server \
  --env-file .env \
  mcp-sse-server
```

## API Endpoints

### SSE Endpoint

```bash
# Kết nối SSE cho MCP protocol
curl -N http://localhost:3001/sse

# Với connection ID
curl -N "http://localhost:3001/sse?connection_id=my-client-123"
```

### n8n Webhook

```bash
# Gọi từ n8n workflow
POST http://localhost:3001/n8n/webhook/mcp-system-check

# Request body
{
  "tool": "check_system_abc",
  "params": {
    "query": "Kiểm tra toàn bộ hệ thống"
  }
}
```

### Health Check

```bash
# Health check
curl http://localhost:3001/health

# Liveness probe (K8s)
curl http://localhost:3001/health/live

# Readiness probe (K8s)
curl http://localhost:3001/health/ready
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:3001/metrics
```

### Information

```bash
# Server info
curl http://localhost:3001/info

# List tools
curl http://localhost:3001/tools

# List n8n tools
curl http://localhost:3001/n8n/tools

# List connections
curl http://localhost:3001/connections
```

## Sử dụng với MCP Protocol

### 1. Kết nối SSE

```javascript
const eventSource = new EventSource('http://localhost:3001/sse');

eventSource.addEventListener('connection', (e) => {
  const data = JSON.parse(e.data);
  console.log('Connected:', data);
});

eventSource.addEventListener('message', (e) => {
  const response = JSON.parse(e.data);
  console.log('MCP Response:', response);
});

eventSource.addEventListener('heartbeat', (e) => {
  console.log('Heartbeat:', e.data);
});
```

### 2. Initialize MCP

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

### 3. List Tools

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### 4. Call Tool

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "check_system_abc",
    "arguments": {
      "query": "Kiểm tra toàn bộ hệ thống"
    }
  }
}
```

## Natural Language Examples

Tool `check_system_abc` hỗ trợ natural language queries:

### Tiếng Việt

```json
{"query": "Kiểm tra toàn bộ hệ thống"}
{"query": "Xem logs 24h gần đây"}
{"query": "Kiểm tra user status và services"}
{"query": "Lấy metrics hiện tại"}
{"query": "Tìm lỗi trong logs 1 giờ qua"}
```

### English

```json
{"query": "Check all systems"}
{"query": "Get recent logs from last 24 hours"}
{"query": "Check user status and services"}
{"query": "Get current metrics"}
{"query": "Search for errors in logs from last hour"}
```

## n8n Workflow Setup

### 1. Tạo Webhook Node trong n8n

```
Workflow: MCP System Check
├── Webhook (Trigger)
│   Path: mcp-system-check
│   Method: POST
│
├── Function (Parse Input)
│   // Extract query and params
│
├── HTTP Request (Call MCP Server)
│   URL: http://mcp-server:3001/n8n/webhook/mcp-system-check
│   Method: POST
│   Body: {{$json}}
│
├── IF (Check Success)
│   Condition: {{$json.success}} === true
│
├── Send Email / Slack Notification
│   Success: ✅ System check passed
│   Error: ❌ System check failed
│
└── End
```

### 2. Trigger từ n8n Schedule

```
Workflow: Daily System Check
├── Schedule (Trigger)
│   Cron: 0 9 * * * (9 AM daily)
│
├── HTTP Request
│   URL: http://mcp-server:3001/n8n/webhook/mcp-system-check
│   Body:
│   {
│     "tool": "check_system_abc",
│     "params": {
│       "query": "Kiểm tra toàn bộ hệ thống"
│     }
│   }
│
└── Process results...
```

## Monitoring

### Prometheus Metrics

Server expose các metrics sau:

- `mcp_requests_total` - Total requests
- `mcp_request_duration_seconds` - Request duration
- `mcp_sse_connections_active` - Active SSE connections
- `mcp_tool_executions_total` - Tool executions

### Grafana Dashboard

Nếu dùng docker-compose, Grafana có sẵn tại:
- URL: http://localhost:3000
- User: `admin`
- Pass: `admin`

Import Prometheus datasource: `http://prometheus:9090`

## Development

### Run Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

### Code Formatting

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Production Deployment

### Docker Compose (Recommended)

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Scale workers
docker-compose up -d --scale mcp-server=3
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-sse-server:latest
        ports:
        - containerPort: 3001
        env:
        - name: ABC_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: abc-api-key
        livenessProbe:
          httpGet:
            path: /health/live
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_HOST` | Server host | `0.0.0.0` |
| `MCP_SERVER_PORT` | Server port | `3001` |
| `MCP_SERVER_WORKERS` | Number of workers | `4` |
| `ABC_SYSTEM_BASE_URL` | ABC System API URL | Required |
| `ABC_API_KEY` | ABC System API key | Required |
| `ABC_TIMEOUT` | API timeout (seconds) | `30` |
| `N8N_INSTANCE_URL` | n8n instance URL | Required |
| `N8N_API_KEY` | n8n API key | Optional |
| `SSE_HEARTBEAT_INTERVAL` | SSE heartbeat interval | `30` |
| `SSE_MAX_CONNECTIONS` | Max SSE connections | `100` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Troubleshooting

### 1. Connection refused

```bash
# Kiểm tra server đang chạy
curl http://localhost:3001/health

# Kiểm tra logs
docker-compose logs mcp-server
```

### 2. API timeouts

```bash
# Tăng timeout trong .env
ABC_TIMEOUT=60

# Restart server
docker-compose restart mcp-server
```

### 3. SSE không kết nối được

```bash
# Kiểm tra CORS settings
# Kiểm tra firewall/proxy
# Kiểm tra browser console
```

### 4. n8n webhook không hoạt động

```bash
# Kiểm tra n8n có thể access được MCP server
curl -X POST http://localhost:3001/n8n/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"tool": "check_system_abc", "params": {"query": "test"}}'
```

## Security Best Practices

1. **API Keys**: Luôn dùng environment variables, không commit vào git
2. **CORS**: Configure CORS cho production (`allow_origins` trong main.py)
3. **Rate Limiting**: Implement rate limiting cho webhooks
4. **HTTPS**: Dùng HTTPS cho production (reverse proxy như nginx)
5. **Authentication**: Thêm authentication cho sensitive endpoints

## License

MIT License

## Support

- Issues: GitHub Issues
- Email: support@example.com
- Documentation: [MCP Protocol Docs](https://modelcontextprotocol.io)

## Changelog

### v1.0.0 (2024-01-17)
- Initial release
- MCP protocol support với SSE
- n8n integration
- 5 ABC System APIs
- Natural language support (VI/EN)
- Prometheus metrics
- Docker support
