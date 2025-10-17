# 🔍 MCP Server Testing Options

Các cách khác nhau để test MCP server - không bắt buộc phải local!

---

## 📋 So sánh các cách test

| Option | Cách | Yêu cầu | Ưu điểm | Nhược điểm |
|--------|------|--------|--------|-----------|
| **1. Curl/Direct** | Terminal commands | Không gì | Nhanh, simple | Không interactive |
| **2. n8n Local** | n8n npm local | n8n + network | Full features | Cần cài local |
| **3. n8n Docker** | n8n trong Docker | Docker | Isolated | Cần Docker |
| **4. n8n Cloud** | n8n.cloud | Internet | Không cần cài | Tạo account |
| **5. n8n Production** | n8n-prod server | SSH access | Production ready | Phức tạp |
| **6. Postman/Insomnia** | API client | App | GUI, easy | Chỉ HTTP |
| **7. MCP Client libs** | Python/JS SDK | Dev env | Programmatic | Cần code |

---

## 🚀 Option 1: Test với Curl (Recommended - Nhanh nhất)

**Không cần cài gì thêm! Chỉ cần MCP server chạy:**

```bash
# 1. Start Mock API
cd mock-api
python3 server.py

# 2. Start MCP Server (terminal mới)
cd ..
python3 src/main.py

# 3. Test (terminal khác)
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{
    "tool": "check_system_abc",
    "params": {
      "query": "Kiểm tra toàn bộ hệ thống"
    }
  }' | jq
```

**✅ Ưu điểm:**
- Không cần cài n8n
- Không cần network phức tạp
- Nhanh nhất
- Dễ debug

**❌ Nhược điểm:**
- Không có UI
- Không thể test workflow complex

---

## 🐳 Option 2: n8n Local + Docker (Recommended cho production)

**Docker Compose tự động setup:**

```bash
./demo-start.sh
```

**Services:**
- Mock API: http://localhost:8000
- MCP Server: http://localhost:3001
- n8n: http://localhost:5678
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Tất cả trong Docker - cùng network tự động!**

---

## 📱 Option 3: n8n Cloud (Không cần cài local)

**Cách dễ nhất nếu MCP server public:**

### Bước 1: Deploy MCP lên server public
```bash
# Follow DEPLOY_UBUNTU.md
# MCP accessible tại: https://mcp.yourdomain.com
```

### Bước 2: n8n Cloud
```
1. Đi: https://app.n8n.cloud
2. Tạo account
3. Create workflow
4. Add MCP Client node
5. Connect tới: https://mcp.yourdomain.com/sse
6. Test!
```

**✅ Ưu điểm:**
- Không cần cài n8n
- Cloud-based
- Easy sharing
- Auto-scaling

**❌ Nhược điểm:**
- Subscription ($)
- MCP phải public
- Internet required

---

## 💻 Option 4: n8n Local npm (Nhẹ nhất)

**Nếu chỉ muốn test, không cần Docker:**

```bash
# Install n8n
npm install -g n8n

# Start n8n
n8n

# Access: http://localhost:5678
```

**Workflow setup:**
```
1. Manual Trigger
2. MCP Client (Initialize)
   - URL: http://localhost:3001/sse
3. MCP Client (Call Tool)
4. Execute
```

**✅ Ưu điểm:**
- Lightweight
- Nhanh setup
- Easy uninstall

**❌ Nhược điểm:**
- Cần npm
- Cần localhost access
- Performance kém hơn Docker

---

## 🌐 Option 5: n8n trong Docker riêng (Best isolation)

```bash
# Start chỉ n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# MCP chạy ở host
python3 src/main.py

# Access: http://localhost:5678

# Trong n8n workflow:
# URL: http://host.docker.internal:3001/sse
```

---

## 📡 Option 6: Postman/Insomnia (Quick visual test)

**Download:** https://www.postman.com/ hoặc https://insomnia.rest/

**Setup:**
```
Method: POST
URL: http://localhost:3001/n8n/webhook/demo
Headers: Content-Type: application/json
Body:
{
  "tool": "check_system_abc",
  "params": {
    "query": "Check all systems"
  }
}
```

**Send → See result!**

**✅ Ưu điểm:**
- Visual
- Easy to test
- Save queries

**❌ Nhược điểm:**
- Chỉ HTTP
- Không test MCP protocol

---

## 🐍 Option 7: Python/JavaScript SDK (Programmatic)

**Test bằng code:**

### Python
```python
import requests

response = requests.post(
    'http://localhost:3001/n8n/webhook/demo',
    json={
        'tool': 'check_system_abc',
        'params': {
            'query': 'Check all systems'
        }
    }
)

print(response.json())
```

### JavaScript
```javascript
const response = await fetch('http://localhost:3001/n8n/webhook/demo', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'check_system_abc',
    params: {
      query: 'Check all systems'
    }
  })
});

const data = await response.json();
console.log(data);
```

---

## 🎯 Recommendations

### Untuk Testing/Development:
```
1. Curl commands (fastest)
2. n8n Local Docker (easy)
3. Postman (visual)
```

### Untuk Production:
```
1. Deploy MCP lên server
2. n8n Cloud hoặc self-hosted
3. MCP Client nodes
```

### Tanpa Local n8n:
```
Option A: Curl/API clients
Option B: Deploy MCP + n8n Cloud
Option C: n8n production server
```

---

## 🔄 Workflow Testing Progression

```
1. Curl test
   ↓ (Works?)
2. Postman/Insomnia
   ↓ (Works?)
3. n8n Local Docker
   ↓ (Works?)
4. n8n Production
   ↓ (Works?)
5. Deploy to production
```

---

## 📝 My Recommendation for You

**Based on your setup:**

```bash
# Terminal 1: Mock API
cd mock-api
python3 server.py

# Terminal 2: MCP Server
cd ..
python3 src/main.py

# Terminal 3: Test dengan curl
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{"tool": "check_system_abc", "params": {"query": "Check all systems"}}' | jq

# Terminal 4 (Optional): n8n Local
n8n
# http://localhost:5678
```

**Atau one-command:**
```bash
./demo-start.sh
```

---

## 🚀 To Test with n8n-prod.iconiclogs.com (Your server)

### Without local n8n:

**1. Deploy MCP lên server:**
```bash
cd /opt/apps/mcpwn8n
docker compose up -d --build
```

**2. Setup reverse proxy trong aaPanel:**
```
Domain: mcp.yourdomain.com
Target: http://127.0.0.1:3001
```

**3. In n8n-prod, add MCP Client:**
```
URL: https://mcp.yourdomain.com/sse
```

**Done! Không cần local setup!**

---

## ✅ No Local n8n Setup:

```
1. MCP Server chạy (bất kỳ đâu - cloud, server, local)
2. MCP accessible qua internet
3. Use n8n Cloud (app.n8n.cloud)
4. Connect tới MCP URL
5. Test workflows
```

---

## 🎓 Summary

| Bạn muốn | Cách |
|----------|------|
| **Test nhanh** | `curl + MCP` |
| **Visual testing** | `Postman + MCP` |
| **Full workflow** | `Docker + n8n Local` |
| **No local setup** | `MCP Server + n8n Cloud` |
| **Production** | `MCP on server + aaPanel + n8n prod` |

---

**Choose your path! Bạn không bắt buộc phải cài n8n local! 🚀**
