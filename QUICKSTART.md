# 🚀 QUICK START - 5 phút setup

## Cách nhanh nhất để chạy demo (3 lệnh)

```bash
cd mcp-sse-server-python

# 1. Start demo
./demo-start.sh

# 2. Test (optional)
./test-demo.sh

# 3. Stop khi xong
docker-compose -f docker-compose.dev.yml down
```

That's it! 🎉

---

## Chi tiết từng bước

### Bước 1: Start Demo

```bash
./demo-start.sh
```

Script này sẽ:
- ✅ Check Docker đang chạy
- ✅ Build và start 4 services (Mock API, MCP Server, Prometheus, Grafana)
- ✅ Wait cho services healthy
- ✅ Show quick test commands

**Thời gian:** ~30-60 giây (lần đầu build, sau đó nhanh hơn)

### Bước 2: Test thử

**Test đơn giản nhất:**
```bash
curl http://localhost:3001/health
```

Kết quả:
```json
{
  "status": "healthy",
  "server": "mcp-sse-server-python",
  "version": "1.0.0",
  "active_connections": 0,
  "registered_tools": 1
}
```

**Test system check với Tiếng Việt:**
```bash
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{"tool": "check_system_abc", "params": {"query": "Kiểm tra toàn bộ hệ thống"}}' \
  | jq
```

**Test system check với English:**
```bash
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{"tool": "check_system_abc", "params": {"query": "Check all systems"}}' \
  | jq
```

### Bước 3: Xem kết quả

Kết quả sẽ có format như này:

```json
{
  "success": true,
  "data": {
    "health": {
      "status": "healthy",
      "uptime_seconds": 1234567,
      "services": {...}
    },
    "users": {
      "total": 5,
      "active": 4,
      "users": [...]
    },
    "services": {
      "total": 5,
      "running": 4,
      "services": [...]
    },
    "logs": {
      "total": 100,
      "entries": [...]
    },
    "metrics": {
      "cpu_usage": 45.23,
      "memory_usage": 67.89,
      ...
    },
    "summary": {
      "checks_performed": ["health", "users", "services", "logs", "metrics"],
      "total_checks": 5,
      "errors_count": 0
    }
  },
  "execution_time_ms": 123.45
}
```

---

## Các queries ví dụ

### Tiếng Việt

```bash
# Kiểm tra toàn bộ
{"query": "Kiểm tra toàn bộ hệ thống"}

# Chỉ logs
{"query": "Xem logs 24h gần đây"}

# Chỉ metrics
{"query": "Lấy metrics hiện tại"}

# User và services
{"query": "Kiểm tra user status và services"}

# Tìm lỗi
{"query": "Tìm lỗi trong logs 1 giờ qua"}
```

### English

```bash
# Check everything
{"query": "Check all systems"}

# Only logs
{"query": "Get logs from last 24 hours"}

# Only metrics
{"query": "Get current system metrics"}

# Users and services
{"query": "Check user status and services"}

# Find errors
{"query": "Search for errors in recent logs"}
```

---

## Web UI Demo

### Mở Grafana
```bash
open http://localhost:3000
# Login: admin / admin
```

### Mở Prometheus
```bash
open http://localhost:9090
```

### Xem Mock API docs
```bash
open http://localhost:8000/docs
```

### Xem MCP Server info
```bash
open http://localhost:3001/info
```

---

## Test SSE Connection

### Với curl
```bash
curl -N http://localhost:3001/sse
```

Bạn sẽ thấy:
```
event: connection
data: {"type":"connection","connection_id":"...","timestamp":"..."}

event: heartbeat
data: {"type":"heartbeat","timestamp":"..."}
...
```

### Với Browser Console

```javascript
const eventSource = new EventSource('http://localhost:3001/sse');

eventSource.addEventListener('connection', (e) => {
  console.log('Connected:', JSON.parse(e.data));
});

eventSource.addEventListener('heartbeat', (e) => {
  console.log('Heartbeat:', JSON.parse(e.data));
});
```

---

## Automated Testing

Chạy toàn bộ test suite:

```bash
./test-demo.sh
```

Output sẽ show:
- ✅ Mock API tests (5 APIs)
- ✅ MCP Server tests (health, info, tools)
- ✅ n8n Webhook tests (Vietnamese & English)
- ✅ Natural Language parsing tests

---

## View Logs

```bash
# Tất cả services
docker-compose -f docker-compose.dev.yml logs -f

# Chỉ MCP Server
docker-compose -f docker-compose.dev.yml logs -f mcp-server

# Chỉ Mock API
docker-compose -f docker-compose.dev.yml logs -f mock-api
```

---

## Troubleshooting

### Services không start?

```bash
# Check Docker
docker info

# Check containers
docker-compose -f docker-compose.dev.yml ps

# Xem logs
docker-compose -f docker-compose.dev.yml logs
```

### Port bị chiếm?

```bash
# Tìm process
lsof -i :3001
lsof -i :8000

# Kill nếu cần
kill -9 <PID>
```

### Restart services

```bash
# Restart tất cả
docker-compose -f docker-compose.dev.yml restart

# Restart từng service
docker-compose -f docker-compose.dev.yml restart mcp-server
```

### Clean restart

```bash
# Stop và xóa containers
docker-compose -f docker-compose.dev.yml down

# Start lại
./demo-start.sh
```

---

## Next Steps

1. ✅ Demo đã chạy thành công
2. 📖 Đọc [DEMO.md](DEMO.md) để xem thêm examples
3. 📚 Đọc [README.md](README.md) cho full documentation
4. 🔧 Custom tools trong `src/tools/`
5. 🚀 Deploy production với `docker-compose.yml`

---

## Cheat Sheet

```bash
# Start
./demo-start.sh

# Test
curl http://localhost:3001/health

# Full test
./test-demo.sh

# Logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.dev.yml down

# Clean everything
docker-compose -f docker-compose.dev.yml down -v
```

---

Enjoy! 🎉
