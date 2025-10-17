# 👋 START HERE

## Chào mừng đến với MCP SSE Server Python!

Đây là một **production-ready MCP Server** với đầy đủ tính năng, sẵn sàng để demo ngay!

---

## 🎯 Bạn muốn làm gì?

### 🚀 Deploy lên Ubuntu server → [DEPLOY_QUICK.md](DEPLOY_QUICK.md)

**Nếu bạn muốn:**
- ✅ Deploy production lên Ubuntu server
- ✅ Dùng với aaPanel
- ✅ Setup trong 5 phút

**👉 Xem:** [DEPLOY_QUICK.md](DEPLOY_QUICK.md) hoặc [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md) (chi tiết)

---

### 1️⃣ Chạy demo ngay (5 phút) → [QUICKSTART.md](QUICKSTART.md)

**Nếu bạn muốn:**
- ✅ Xem nó hoạt động như thế nào
- ✅ Test ngay không cần setup gì phức tạp
- ✅ Không có API thật để test

**👉 Chỉ cần chạy:**
```bash
./demo-start.sh
```

---

### 2️⃣ Xem chi tiết demo → [DEMO.md](DEMO.md)

**Nếu bạn muốn:**
- ✅ Xem tất cả commands có thể test
- ✅ Hiểu cách test từng tính năng
- ✅ Test với natural language (Tiếng Việt & English)
- ✅ Setup monitoring dashboard

**👉 Đọc:** [DEMO.md](DEMO.md)

---

### 3️⃣ Hiểu toàn bộ project → [README.md](README.md)

**Nếu bạn muốn:**
- ✅ Hiểu kiến trúc hệ thống
- ✅ Deploy production với API thật
- ✅ Tích hợp với n8n instance thật
- ✅ Customize và extend features

**👉 Đọc:** [README.md](README.md)

---

### 4️⃣ Overview nhanh → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**Nếu bạn muốn:**
- ✅ Xem tổng quan dự án
- ✅ Biết tech stack
- ✅ Hiểu cấu trúc code
- ✅ Use cases

**👉 Đọc:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🚀 Recommended Path

### Cho người mới:
```
1. QUICKSTART.md  → Chạy demo
2. DEMO.md        → Test features
3. README.md      → Full docs (khi cần)
```

### Cho developers:
```
1. PROJECT_SUMMARY.md  → Overview
2. README.md           → Architecture
3. Source code         → Implementation
```

### Cho DevOps:
```
1. README.md           → Deployment guide
2. Docker files        → Container setup
3. Monitoring          → Prometheus/Grafana
```

---

## ⚡ Ultra Quick Start

**Muốn chạy NGAY? 3 lệnh:**

```bash
cd mcp-sse-server-python
./demo-start.sh          # Start demo
./test-demo.sh           # Run tests
```

**Xong!** Bạn đã có:
- ✅ Mock API server (5 APIs)
- ✅ MCP SSE Server
- ✅ Prometheus metrics
- ✅ Grafana dashboard

---

## 📁 Files trong project

| File | Khi nào đọc |
|------|-------------|
| **START_HERE.md** | Đầu tiên (you are here!) |
| **QUICKSTART.md** | Muốn chạy demo ngay |
| **DEMO.md** | Muốn test chi tiết |
| **README.md** | Muốn hiểu đầy đủ |
| **PROJECT_SUMMARY.md** | Muốn overview |
| **demo-start.sh** | Script để chạy demo |
| **test-demo.sh** | Script để test tự động |

---

## 🎓 What is this project?

Đây là một **MCP (Model Context Protocol) Server** với:

### Core Features:
- 🔄 **SSE Transport** - Real-time bidirectional communication
- 🤖 **MCP Protocol** - JSON-RPC 2.0 implementation
- 🌐 **5 ABC System APIs** - Health, Users, Services, Logs, Metrics
- 🗣️ **Natural Language** - Supports Vietnamese & English
- 📊 **n8n Integration** - Webhook endpoints
- 📈 **Monitoring** - Prometheus + Grafana

### Why use it?
- ✅ Aggregate multiple APIs với natural language
- ✅ Automate system checks với n8n workflows
- ✅ Monitor systems với friendly queries
- ✅ Integrate with AI tools (Claude, etc.)

---

## 🎯 First Steps

### Step 1: Chọn path của bạn

**Path A: Demo Mode** (recommended cho lần đầu)
```bash
./demo-start.sh
```
→ Xem [QUICKSTART.md](QUICKSTART.md)

**Path B: Production Mode** (có API thật)
```bash
# 1. Copy .env
cp .env.example .env

# 2. Edit với API credentials thật
nano .env

# 3. Run
docker-compose up -d
```
→ Xem [README.md](README.md)

### Step 2: Test thử

```bash
# Simple health check
curl http://localhost:3001/health

# Or run full test suite
./test-demo.sh
```

### Step 3: Explore!

- 🌐 MCP Server: http://localhost:3001
- 📊 Mock API: http://localhost:8000
- 📈 Prometheus: http://localhost:9090
- 📉 Grafana: http://localhost:3000

---

## ❓ FAQ

**Q: Tôi không có API thật, có test được không?**
A: Có! Dùng Mock API - chạy `./demo-start.sh`

**Q: Cần cài gì không?**
A: Chỉ cần Docker Desktop. Không cần cài Python hay dependencies gì khác.

**Q: Mất bao lâu để setup?**
A: ~1-2 phút (lần đầu build Docker image), sau đó <30 giây.

**Q: Có tích hợp với n8n thật không?**
A: Có, xem phần n8n integration trong README.md

**Q: Có production-ready không?**
A: Có! Đầy đủ error handling, monitoring, health checks, Docker support.

**Q: Support ngôn ngữ gì?**
A: Tiếng Việt và English cho natural language queries.

---

## 🆘 Need Help?

**Gặp lỗi?**
1. Xem [DEMO.md](DEMO.md) → Troubleshooting section
2. Check logs: `docker-compose -f docker-compose.dev.yml logs`
3. Restart: `./demo-start.sh`

**Muốn học thêm?**
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Explore source code in `src/`
3. Check MCP spec: https://modelcontextprotocol.io

---

## 🎉 Ready?

Chọn path của bạn:

→ **Quick Demo:** [QUICKSTART.md](QUICKSTART.md)

→ **Detailed Guide:** [DEMO.md](DEMO.md)

→ **Full Docs:** [README.md](README.md)

→ **Overview:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Let's go! 🚀**

```bash
./demo-start.sh
```
