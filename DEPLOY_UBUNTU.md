# 🚀 Deploy MCP Server lên Ubuntu Server

Hướng dẫn deploy MCP SSE Server lên Ubuntu server (với aaPanel)

---

## 📋 Yêu cầu Server

- **OS:** Ubuntu 20.04+ / Debian 10+
- **RAM:** Minimum 2GB (Recommended 4GB)
- **CPU:** 2 cores+
- **Disk:** 20GB+
- **Docker:** Version 20.10+
- **Docker Compose:** Version 2.0+

---

## 🔧 Bước 1: Chuẩn bị Server

### SSH vào server
```bash
ssh root@your-server-ip
# hoặc
ssh username@your-server-ip
```

### Update system
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Docker
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### (Optional) Add user to docker group
```bash
# Để không cần sudo mỗi lần chạy docker
sudo usermod -aG docker $USER
newgrp docker

# Test without sudo
docker ps
```

---

## 📦 Bước 2: Clone Repository

```bash
# Tạo thư mục cho project
mkdir -p /opt/apps
cd /opt/apps

# Clone repository
git clone https://github.com/nguyenxtan/mcpwn8n.git
cd mcpwn8n

# Check files
ls -la
```

---

## ⚙️ Bước 3: Configuration

### Tạo file .env cho production
```bash
# Copy từ template
cp .env.example .env

# Edit với nano hoặc vi
nano .env
```

### Cấu hình .env (Quan trọng!)
```bash
# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=3001
MCP_SERVER_WORKERS=4

# ABC System Configuration - THAY ĐỔI THEO HỆ THỐNG THẬT
ABC_SYSTEM_BASE_URL=https://your-abc-api.com
ABC_API_KEY=your_real_api_key_here
ABC_TIMEOUT=30
ABC_MAX_RETRIES=3
ABC_RETRY_BACKOFF=1.0

# n8n Integration - THAY ĐỔI THEO n8n INSTANCE
N8N_INSTANCE_URL=n8n-prod.iconiclogs.com
N8N_API_KEY=your_n8n_api_key_here
N8N_WEBHOOK_PATH=mcp-system-check

# SSE Configuration
SSE_HEARTBEAT_INTERVAL=30
SSE_RECONNECT_TIMEOUT=5
SSE_MAX_CONNECTIONS=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Environment
ENVIRONMENT=production
```

**Lưu file:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🐳 Bước 4: Deploy với Docker Compose

### Option A: Production (API thật)

```bash
# Build và start
docker compose up -d --build

# Xem logs
docker compose logs -f

# Check status
docker compose ps
```

### Option B: Demo Mode (Mock API)

```bash
# Nếu muốn test với Mock API trước
docker compose -f docker-compose.dev.yml up -d --build

# Xem logs
docker compose -f docker-compose.dev.yml logs -f
```

---

## ✅ Bước 5: Verify Deployment

### Check containers đang chạy
```bash
docker compose ps
```

Output mong đợi:
```
NAME                IMAGE                  STATUS
mcp-sse-server      mcp-sse-server:latest  Up 2 minutes (healthy)
mcp-prometheus      prom/prometheus        Up 2 minutes
mcp-grafana         grafana/grafana        Up 2 minutes
```

### Test health endpoint
```bash
curl http://localhost:3001/health
```

Output:
```json
{
  "status": "healthy",
  "server": "mcp-sse-server-python",
  "version": "1.0.0",
  "active_connections": 0,
  "registered_tools": 1
}
```

### Test với full system check
```bash
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{"tool": "check_system_abc", "params": {"query": "Check all systems"}}' \
  | jq
```

---

## 🌐 Bước 6: Setup với aaPanel (Reverse Proxy)

### 1. Mở aaPanel Dashboard
```
https://your-server-ip:7800
```

### 2. Tạo Site mới
- Website → Add site
- Domain: `mcp.yourdomain.com`
- PHP: Không cần (chọn Static)
- Database: Không cần

### 3. Setup Reverse Proxy
**aaPanel → Website → [Your Site] → Reverse Proxy**

**Target URL:**
```
http://127.0.0.1:3001
```

**Configuration:**
```nginx
# Reverse proxy settings (aaPanel auto-generates)
location / {
    proxy_pass http://127.0.0.1:3001;
    proxy_http_version 1.1;

    # Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # SSE support (IMPORTANT!)
    proxy_set_header Connection '';
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 300s;
}
```

**Lưu ý quan trọng cho SSE:**
- `proxy_buffering off;` - Tắt buffering
- `proxy_cache off;` - Tắt cache
- `chunked_transfer_encoding off;` - Tắt chunked encoding

### 4. SSL Certificate (Let's Encrypt)
**aaPanel → Website → [Your Site] → SSL**
- Chọn "Let's Encrypt"
- Check "Force HTTPS"
- Apply

### 5. Firewall Settings
**aaPanel → Security**
- Port 3001: Không cần mở (internal only)
- Port 80: Mở (HTTP)
- Port 443: Mở (HTTPS)

---

## 📊 Bước 7: Setup Monitoring (Optional)

### Prometheus
Truy cập: `http://your-server-ip:9090`

**aaPanel Setup:**
- Tạo site mới: `prometheus.yourdomain.com`
- Reverse proxy: `http://127.0.0.1:9090`
- Enable SSL

### Grafana
Truy cập: `http://your-server-ip:3000`
Login: `admin` / `admin`

**aaPanel Setup:**
- Tạo site mới: `grafana.yourdomain.com`
- Reverse proxy: `http://127.0.0.1:3000`
- Enable SSL

**Add Prometheus datasource:**
- URL: `http://prometheus:9090`
- Save & Test

---

## 🔄 Bước 8: Auto-restart & Management

### Setup Docker auto-restart
```bash
# Update compose file để auto-restart
docker compose up -d --force-recreate
```

Docker compose mặc định đã có `restart: unless-stopped`

### Useful Commands

**Start services:**
```bash
docker compose up -d
```

**Stop services:**
```bash
docker compose down
```

**Restart services:**
```bash
docker compose restart
```

**Restart chỉ MCP server:**
```bash
docker compose restart mcp-server
```

**View logs:**
```bash
# All services
docker compose logs -f

# Only MCP server
docker compose logs -f mcp-server

# Last 100 lines
docker compose logs --tail=100 mcp-server
```

**Check resource usage:**
```bash
docker stats
```

**Update code và redeploy:**
```bash
cd /opt/apps/mcpwn8n

# Pull latest code
git pull origin main

# Rebuild và restart
docker compose up -d --build

# Check logs
docker compose logs -f mcp-server
```

---

## 🔍 Troubleshooting

### 1. Container không start
```bash
# Check logs
docker compose logs mcp-server

# Check Docker daemon
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

### 2. Port bị chiếm
```bash
# Check port usage
sudo netstat -tulpn | grep 3001

# Kill process nếu cần
sudo kill -9 <PID>
```

### 3. Memory issues
```bash
# Check memory
free -h

# Check Docker memory
docker stats

# Clean Docker system
docker system prune -a
```

### 4. API connection failed
```bash
# Test từ container
docker exec -it mcp-sse-server curl http://localhost:3001/health

# Check network
docker network ls
docker network inspect mcpwn8n_mcp-network
```

### 5. SSE không hoạt động qua aaPanel
- Check nginx config có `proxy_buffering off;`
- Check timeout settings
- Check SSL certificate
- Test trực tiếp: `curl -N http://localhost:3001/sse`

---

## 📈 Performance Tuning

### Tăng workers (nếu server mạnh)
Edit `.env`:
```bash
MCP_SERVER_WORKERS=8  # Tùy số CPU cores
```

Restart:
```bash
docker compose restart mcp-server
```

### Tăng connection limit
Edit `.env`:
```bash
SSE_MAX_CONNECTIONS=200
```

### Docker resource limits
Edit `docker-compose.yml`:
```yaml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🔐 Security Best Practices

### 1. Firewall
```bash
# Install UFW
sudo apt install ufw

# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS (aaPanel handles these)
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 2. Đổi SSH port (recommended)
```bash
sudo nano /etc/ssh/sshd_config
# Đổi Port 22 thành Port 2222
sudo systemctl restart sshd
```

### 3. Secure .env file
```bash
# Set proper permissions
chmod 600 .env

# Không commit .env lên Git
```

### 4. Regular updates
```bash
# System updates
sudo apt update && sudo apt upgrade -y

# Docker updates
sudo apt install docker-ce docker-ce-cli containerd.io

# Pull latest code
cd /opt/apps/mcpwn8n
git pull origin main
docker compose up -d --build
```

---

## 📝 Monitoring & Logs

### Setup log rotation
Create `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
docker compose up -d
```

### Monitor logs với aaPanel
aaPanel → Docker → Containers → View Logs

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Deploy
cd /opt/apps/mcpwn8n
docker compose up -d --build

# Update
git pull origin main
docker compose up -d --build

# Restart
docker compose restart mcp-server

# Logs
docker compose logs -f mcp-server

# Stop
docker compose down

# Clean và restart
docker compose down
docker system prune -f
docker compose up -d --build

# Health check
curl http://localhost:3001/health

# Test API
curl -X POST http://localhost:3001/n8n/webhook/demo \
  -H 'Content-Type: application/json' \
  -d '{"tool": "check_system_abc", "params": {"query": "Check all systems"}}'

# Stats
docker stats mcp-sse-server
```

---

## 📞 Support

**Logs location:**
- Docker logs: `docker compose logs`
- System logs: `/var/log/syslog`
- aaPanel logs: `/www/server/panel/logs/`

**Health endpoints:**
- Main: `http://your-domain/health`
- Liveness: `http://your-domain/health/live`
- Readiness: `http://your-domain/health/ready`
- Metrics: `http://your-domain/metrics`

**Issues:**
- GitHub: https://github.com/nguyenxtan/mcpwn8n/issues

---

## ✅ Deployment Checklist

- [ ] Server đã có Docker & Docker Compose
- [ ] Clone repository
- [ ] Tạo và config file `.env`
- [ ] Build và start containers
- [ ] Test health endpoint
- [ ] Setup reverse proxy trong aaPanel
- [ ] Setup SSL certificate
- [ ] Test SSE connection
- [ ] Setup monitoring (optional)
- [ ] Configure firewall
- [ ] Setup log rotation
- [ ] Document credentials

---

**Done! Server đã sẵn sàng! 🎉**

Access your MCP Server:
- Main: `https://mcp.yourdomain.com`
- Health: `https://mcp.yourdomain.com/health`
- Info: `https://mcp.yourdomain.com/info`
