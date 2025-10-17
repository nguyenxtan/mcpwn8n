# ⚡ Quick Deploy Guide - Ubuntu Server

## TL;DR - Deploy trong 5 phút

```bash
# 1. SSH vào server
ssh root@your-server-ip

# 2. Install Docker (nếu chưa có)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clone repository
cd /opt/apps
git clone https://github.com/nguyenxtan/mcpwn8n.git
cd mcpwn8n

# 4. Config
cp .env.example .env
nano .env  # Chỉnh sửa API keys

# 5. Deploy
docker compose up -d --build

# 6. Verify
curl http://localhost:3001/health
```

**Done! Server đang chạy tại port 3001**

---

## 🔧 Setup aaPanel Reverse Proxy (2 phút)

### 1. Tạo Site
- Domain: `mcp.yourdomain.com`
- Type: Static

### 2. Reverse Proxy
```
Target: http://127.0.0.1:3001
```

### 3. Important: Enable SSE Support
Thêm vào nginx config:
```nginx
proxy_buffering off;
proxy_cache off;
chunked_transfer_encoding off;
```

### 4. SSL
Enable Let's Encrypt trong aaPanel

**Done!** Access: `https://mcp.yourdomain.com`

---

## 📝 File .env cần chỉnh sửa

```bash
# QUAN TRỌNG - Thay đổi những dòng này:
ABC_SYSTEM_BASE_URL=https://your-real-api.com
ABC_API_KEY=your_real_api_key

N8N_INSTANCE_URL=n8n-prod.iconiclogs.com
N8N_API_KEY=your_n8n_api_key

# Giữ nguyên phần còn lại
```

---

## 🔄 Update Code

```bash
cd /opt/apps/mcpwn8n
git pull origin main
docker compose up -d --build
```

---

## 📊 Useful Commands

```bash
# View logs
docker compose logs -f mcp-server

# Restart
docker compose restart mcp-server

# Stop
docker compose down

# Status
docker compose ps

# Resource usage
docker stats mcp-sse-server
```

---

## ✅ Test Endpoints

```bash
# Health check
curl https://mcp.yourdomain.com/health

# System info
curl https://mcp.yourdomain.com/info

# Test tool
curl -X POST https://mcp.yourdomain.com/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{"tool": "check_system_abc", "params": {"query": "Check all systems"}}'

# SSE connection
curl -N https://mcp.yourdomain.com/sse
```

---

## 🆘 Troubleshooting

**Container không start:**
```bash
docker compose logs mcp-server
```

**Không connect được:**
```bash
# Check port
netstat -tulpn | grep 3001

# Check firewall
sudo ufw status
```

**Update không hoạt động:**
```bash
docker compose down
docker system prune -f
git pull origin main
docker compose up -d --build
```

---

## 📚 Full Documentation

Chi tiết xem: [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md)

---

**That's it! Simple & Fast! 🚀**
