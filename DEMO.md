# DEMO MODE - Quick Start Guide

## Chạy Demo với Mock API (Không cần API thật)

Tôi đã tạo sẵn Mock API server giả lập đầy đủ 5 APIs của hệ thống ABC. Bạn có thể test toàn bộ tính năng ngay lập tức!

---

## 🚀 Quick Start (3 bước)

### Bước 1: Clone và khởi động

```bash
cd mcp-sse-server-python

# Khởi động toàn bộ stack (Mock API + MCP Server + Monitoring)
docker-compose -f docker-compose.dev.yml up -d
```

### Bước 2: Kiểm tra services đang chạy

```bash
# Xem logs
docker-compose -f docker-compose.dev.yml logs -f

# Kiểm tra health
curl http://localhost:8000/health      # Mock API
curl http://localhost:3001/health      # MCP Server
```

### Bước 3: Test các endpoints!

Xem phần [Demo Commands](#demo-commands) bên dưới.

---

## 📋 Services đang chạy

| Service | Port | URL | Mô tả |
|---------|------|-----|-------|
| **Mock API** | 8000 | http://localhost:8000 | Giả lập ABC System APIs |
| **MCP Server** | 3001 | http://localhost:3001 | MCP protocol với SSE |
| **Prometheus** | 9090 | http://localhost:9090 | Metrics collection |
| **Grafana** | 3000 | http://localhost:3000 | Metrics visualization (admin/admin) |

---

## 🧪 Demo Commands

### 1. Test Mock API trực tiếp

```bash
# API 1: Health check
curl http://localhost:8000/api/system/health | jq

# API 2: User status
curl http://localhost:8000/api/users/status | jq

# API 3: Services list
curl http://localhost:8000/api/services/list | jq

# API 4: Query logs
curl -X POST http://localhost:8000/api/logs/query \
  -H "Content-Type: application/json" \
  -d '{"timeframe": "1h", "limit": 10}' | jq

# API 5: Current metrics
curl http://localhost:8000/api/metrics/current | jq
```

### 2. Test MCP Server Info

```bash
# Server info
curl http://localhost:3001/info | jq

# List tools
curl http://localhost:3001/tools | jq

# List n8n tools
curl http://localhost:3001/n8n/tools | jq

# Active connections
curl http://localhost:3001/connections | jq

# Prometheus metrics
curl http://localhost:3001/metrics
```

### 3. Test SSE Connection

```bash
# Kết nối SSE (sẽ stream events)
curl -N http://localhost:3001/sse

# Hoặc với connection ID
curl -N "http://localhost:3001/sse?connection_id=demo-123"
```

### 4. Test n8n Webhook với Natural Language

**Tiếng Việt:**
```bash
# Kiểm tra toàn bộ hệ thống
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Kiểm tra toàn bộ hệ thống"
    }
  }' | jq

# Xem logs 24h gần đây
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Xem logs 24h gần đây"
    }
  }' | jq

# Kiểm tra user và services
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Kiểm tra user status và services"
    }
  }' | jq

# Tìm lỗi trong logs
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Tìm lỗi trong logs 1 giờ qua"
    }
  }' | jq
```

**English:**
```bash
# Check all systems
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Check all systems"
    }
  }' | jq

# Get recent logs
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Get logs from last 24 hours"
    }
  }' | jq

# Check metrics
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Get current system metrics"
    }
  }' | jq
```

### 5. Test với Filters

```bash
# Query logs với filters cụ thể
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Xem logs",
      "filters": {
        "log_timeframe": "24h",
        "log_level": "error",
        "log_service": "api-gateway"
      }
    }
  }' | jq
```

---

## 📊 Monitoring Dashboard

### Prometheus
- URL: http://localhost:9090
- Queries ví dụ:
  ```
  mcp_requests_total
  mcp_sse_connections_active
  mcp_tool_executions_total
  rate(mcp_requests_total[5m])
  ```

### Grafana
- URL: http://localhost:3000
- Login: `admin` / `admin`
- Add Prometheus datasource: `http://prometheus:9090`
- Import dashboard hoặc tạo dashboard mới với metrics trên

---

## 🔍 Demo Scenarios

### Scenario 1: Full System Check
```bash
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Kiểm tra toàn bộ hệ thống"
    }
  }' | jq
```

**Kết quả mong đợi:**
- Health status của tất cả services
- Danh sách users và session count
- Danh sách services và status
- Recent logs (last 1 hour)
- Current system metrics (CPU, Memory, Disk, Network)

### Scenario 2: Error Investigation
```bash
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Tìm lỗi trong logs 24h gần đây"
    }
  }' | jq
```

### Scenario 3: Performance Monitoring
```bash
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Check system performance metrics"
    }
  }' | jq
```

---

## 🧪 Test SSE với Browser/JavaScript

Tạo file `test-sse.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>MCP SSE Demo</title>
</head>
<body>
    <h1>MCP SSE Connection Test</h1>
    <div id="status">Disconnected</div>
    <div id="events"></div>

    <script>
        const eventSource = new EventSource('http://localhost:3001/sse');
        const statusDiv = document.getElementById('status');
        const eventsDiv = document.getElementById('events');

        eventSource.addEventListener('connection', (e) => {
            const data = JSON.parse(e.data);
            statusDiv.textContent = 'Connected: ' + data.connection_id;
            eventsDiv.innerHTML += `<p><strong>Connection:</strong> ${JSON.stringify(data, null, 2)}</p>`;
        });

        eventSource.addEventListener('message', (e) => {
            eventsDiv.innerHTML += `<p><strong>Message:</strong> ${e.data}</p>`;
        });

        eventSource.addEventListener('heartbeat', (e) => {
            const data = JSON.parse(e.data);
            console.log('Heartbeat:', data.timestamp);
        });

        eventSource.onerror = (error) => {
            statusDiv.textContent = 'Error: ' + error;
            console.error('SSE Error:', error);
        };
    </script>
</body>
</html>
```

Mở file trong browser: `open test-sse.html`

---

## 📝 Mock API Data

Mock API trả về data giả lập realistic:

**Services:** 5 services (4 running, 1 degraded)
- api-gateway
- user-service
- payment-service
- notification-service
- analytics-service (degraded)

**Users:** 5 users (4 active, 1 inactive)
- admin (2 sessions)
- john.doe (1 session)
- jane.smith (3 sessions)
- bob.wilson (inactive)
- alice.brown (1 session)

**Logs:** Random generated với 4 levels (debug, info, warning, error)

**Metrics:** Random realistic values
- CPU: 20-80%
- Memory: 40-85%
- Disk: 30-70%
- Network: 10-100 Mbps in, 5-50 Mbps out
- Request rate: 100-1000 req/s
- Error rate: 0.1-5%

---

## 🛠️ Development Mode

### Chạy local (không Docker)

**Terminal 1 - Mock API:**
```bash
cd mock-api
pip install -r requirements.txt
python server.py
```

**Terminal 2 - MCP Server:**
```bash
# Copy .env.dev
cp .env.dev .env

# Install dependencies
pip install -r requirements.txt

# Run server
python src/main.py
```

### Hot Reload Development

Sửa `docker-compose.dev.yml` để mount code:
```yaml
mcp-server:
  volumes:
    - ./src:/app/src
  command: uvicorn src.main:app --host 0.0.0.0 --port 3001 --reload
```

---

## 🐛 Troubleshooting

### Services không start
```bash
# Kiểm tra logs
docker-compose -f docker-compose.dev.yml logs

# Xem status
docker-compose -f docker-compose.dev.yml ps

# Restart
docker-compose -f docker-compose.dev.yml restart
```

### Port đã được sử dụng
```bash
# Tìm process đang dùng port
lsof -i :3001
lsof -i :8000

# Kill process
kill -9 <PID>

# Hoặc đổi port trong docker-compose.dev.yml
```

### Mock API không response
```bash
# Test trực tiếp
docker exec -it abc-mock-api curl http://localhost:8000/health

# Xem logs
docker logs abc-mock-api
```

---

## 🎯 Next Steps

1. **Test với Postman/Insomnia**: Import API collection
2. **Tích hợp với n8n thật**: Setup n8n instance local
3. **Custom tools**: Thêm tools mới vào `src/tools/`
4. **Production deployment**: Dùng `docker-compose.yml` với API thật

---

## 📚 Tài liệu thêm

- [README.md](README.md) - Full documentation
- [MCP Protocol](https://modelcontextprotocol.io) - MCP specification
- [FastAPI Docs](https://fastapi.tiangolo.com) - FastAPI documentation
- [SSE Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html) - SSE specification

---

## 🎉 Enjoy Testing!

Bạn đã có một hệ thống MCP hoàn chỉnh để demo và test. Không cần API thật, mọi thứ đã sẵn sàng!

**Hỗ trợ:**
- Issues: GitHub Issues
- Email: support@example.com
