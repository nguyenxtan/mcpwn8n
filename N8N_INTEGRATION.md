# 🔗 n8n Integration Guide

Hướng dẫn tích hợp MCP Server với n8n instance

---

## 📋 Prerequisites

- n8n instance đang chạy (n8n-prod.iconiclogs.com hoặc local)
- MCP Server đang chạy (localhost:3001 hoặc deployed)
- Network connectivity giữa n8n và MCP server

---

## 🚀 Option 1: Test với n8n Local (Recommended cho test)

### Bước 1: Install n8n local

```bash
# Install n8n
npm install -g n8n

# Hoặc dùng Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Bước 2: Start n8n

```bash
# Nếu dùng npm
n8n

# Access: http://localhost:5678
```

### Bước 3: Tạo Workflow đầu tiên

**Workflow 1: Manual Trigger → MCP Check**

1. **Mở n8n:** http://localhost:5678
2. **Create new workflow**
3. **Add nodes:**

#### Node 1: Manual Trigger
- Tìm và add: "Manual Trigger"
- Để default settings

#### Node 2: HTTP Request (Call MCP)
- Add node: "HTTP Request"
- **Method:** POST
- **URL:** `http://host.docker.internal:3001/n8n/webhook/demo`
  - Nếu n8n chạy local (npm): `http://localhost:3001/n8n/webhook/demo`
  - Nếu n8n trong Docker: `http://host.docker.internal:3001/n8n/webhook/demo`
- **Authentication:** None
- **Body Content Type:** JSON
- **Specify Body:** Using Fields Below
- **JSON/RAW Parameters:**
  ```json
  {
    "tool": "check_system_abc",
    "params": {
      "query": "Kiểm tra toàn bộ hệ thống"
    }
  }
  ```

#### Node 3: IF (Check Success)
- Add node: "IF"
- **Condition:** `{{ $json.success }}` equals `true`

#### Node 4a: Success Path - Set Message
- Add node: "Set" (from IF true branch)
- **Add Field:**
  - Name: `message`
  - Value: `✅ System check passed!`
- **Add Field:**
  - Name: `summary`
  - Value: `{{ $json.data.summary }}`

#### Node 4b: Error Path - Set Error
- Add node: "Set" (from IF false branch)
- **Add Field:**
  - Name: `message`
  - Value: `❌ System check failed!`
- **Add Field:**
  - Name: `error`
  - Value: `{{ $json.error }}`

**Save workflow:** "MCP System Check - Manual"

### Bước 4: Test workflow

1. Click **"Execute Workflow"**
2. Xem kết quả trong "IF" node
3. Check output của node "Set"

---

## 📅 Workflow 2: Schedule Trigger (Auto check hàng ngày)

### Tạo workflow mới:

#### Node 1: Schedule Trigger
- Add: "Schedule Trigger"
- **Trigger Times:** Custom
- **Hour:** 9 (9 AM)
- **Minute:** 0
- **Weekdays:** Monday through Friday
- **Timezone:** Asia/Ho_Chi_Minh

#### Node 2-4: Giống như workflow 1
(HTTP Request → IF → Set)

#### Node 5: Send Email (Optional)
- Add: "Send Email" (after Set nodes)
- **From Email:** your-email@gmail.com
- **To Email:** admin@yourdomain.com
- **Subject:** `Daily System Check - {{ $now.format('DD/MM/YYYY') }}`
- **Text:** `{{ $json.message }}\n\n{{ JSON.stringify($json.summary, null, 2) }}`

**Save:** "MCP System Check - Daily"

---

## 🌐 Option 2: Test với n8n Production (n8n-prod.iconiclogs.com)

### Bước 1: Expose MCP Server

**Option A: Deploy MCP lên server public**
- Follow [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md)
- MCP server cần accessible từ n8n instance

**Option B: Ngrok (cho test)**
```bash
# Install ngrok
brew install ngrok

# Expose MCP server
ngrok http 3001

# Copy URL: https://xxxx-xxxx-xxxx.ngrok-free.app
```

### Bước 2: Tạo workflow trong n8n-prod

1. Login vào n8n-prod.iconiclogs.com
2. Tạo workflow như Option 1
3. **URL trong HTTP Request node:**
   ```
   https://your-mcp-server.com/n8n/webhook/demo
   # hoặc ngrok URL
   https://xxxx-xxxx.ngrok-free.app/n8n/webhook/demo
   ```

---

## 🔔 Workflow 3: Webhook Trigger (Từ external system)

### Tạo workflow:

#### Node 1: Webhook Trigger
- Add: "Webhook"
- **HTTP Method:** POST
- **Path:** `mcp-check`
- Copy webhook URL: `https://n8n-prod.iconiclogs.com/webhook/mcp-check`

#### Node 2: Function (Parse Input)
- Add: "Function"
- **JavaScript Code:**
```javascript
// Parse input from webhook
const query = $input.item.json.query || "Check all systems";
const filters = $input.item.json.filters || {};

return {
  json: {
    tool: "check_system_abc",
    params: {
      query: query,
      filters: filters
    }
  }
};
```

#### Node 3-5: HTTP Request → IF → Set
(Giống workflow 1)

#### Node 6: Respond to Webhook
- Add: "Respond to Webhook"
- **Response Body:** `{{ JSON.stringify($json) }}`

**Save:** "MCP Webhook Handler"

### Test webhook:

```bash
curl -X POST https://n8n-prod.iconiclogs.com/webhook/mcp-check \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Kiểm tra toàn bộ hệ thống"
  }'
```

---

## 📊 Workflow 4: Advanced - Multiple Checks với Loop

### Tạo workflow kiểm tra nhiều queries:

#### Node 1: Manual Trigger

#### Node 2: Set (Define Queries)
- Add: "Set"
- **Mode:** Manual Mapping
- **Add Value:**
```json
{
  "queries": [
    "Check system health",
    "Get user status",
    "Check services",
    "View recent logs",
    "Get metrics"
  ]
}
```

#### Node 3: Split In Batches
- Add: "Split In Batches"
- **Batch Size:** 1
- **Options → Reset:** true

#### Node 4: Function (Get Current Query)
```javascript
const queries = $('Set').item.json.queries;
const index = $input.context.noItemsLeft;
const query = queries[index];

return {
  json: {
    tool: "check_system_abc",
    params: {
      query: query
    }
  }
};
```

#### Node 5: HTTP Request → IF → Set
(Giống workflow 1)

#### Node 6: Loop back to Split In Batches
Connect node Set back to "Split In Batches"

**Save:** "MCP Multiple Checks"

---

## 🎨 Workflow 5: Error Monitoring với Slack/Email

### Setup:

#### Node 1: Schedule (Every hour)
- **Trigger Times:** Every Hour

#### Node 2: HTTP Request (Check for errors)
```json
{
  "tool": "check_system_abc",
  "params": {
    "query": "Tìm lỗi trong logs 1 giờ qua",
    "filters": {
      "log_level": "error"
    }
  }
}
```

#### Node 3: IF (Has Errors?)
- **Condition:** `{{ $json.data.logs.total }}` > 0

#### Node 4: Slack (Send Alert)
- Add: "Slack"
- **Resource:** Message
- **Channel:** #alerts
- **Text:**
```
⚠️ *Error Alert*
Found {{ $json.data.logs.total }} errors in the last hour!

Top errors:
{{ $json.data.logs.entries.slice(0, 5).map(e => `- ${e.message}`).join('\n') }}
```

#### Node 5: Email (Send to Admin)
- **Subject:** `🚨 Error Alert - {{ $json.data.logs.total }} errors detected`
- **Text:** Similar to Slack message

**Save:** "MCP Error Monitor"

---

## 🔧 Workflow Templates (Import vào n8n)

### Template 1: Basic System Check

```json
{
  "name": "MCP Basic System Check",
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:3001/n8n/webhook/demo",
        "options": {},
        "bodyParametersJson": "{\n  \"tool\": \"check_system_abc\",\n  \"params\": {\n    \"query\": \"Check all systems\"\n  }\n}"
      },
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "HTTP Request"}]]
    }
  }
}
```

**Import:**
1. Copy JSON trên
2. n8n → Workflows → Import from URL or File
3. Paste JSON
4. Save

---

## 🧪 Testing Checklist

### Local Testing:
- [ ] MCP Server đang chạy (port 3001)
- [ ] Mock API đang chạy (port 8000)
- [ ] n8n đang chạy (port 5678)
- [ ] Test Manual Trigger workflow
- [ ] Verify kết quả trong n8n

### Production Testing:
- [ ] MCP Server deployed và accessible
- [ ] n8n có thể reach MCP server
- [ ] Test với Webhook Trigger
- [ ] Setup Schedule Trigger
- [ ] Configure error alerts

---

## 📝 Example Queries cho n8n

### Vietnamese:
```json
{"query": "Kiểm tra toàn bộ hệ thống"}
{"query": "Xem logs 24h gần đây"}
{"query": "Kiểm tra user status"}
{"query": "Lấy metrics hiện tại"}
{"query": "Tìm lỗi trong logs"}
```

### English:
```json
{"query": "Check all systems"}
{"query": "Get logs from last 24 hours"}
{"query": "Check user status"}
{"query": "Get current metrics"}
{"query": "Search for errors in logs"}
```

### With Filters:
```json
{
  "query": "Xem logs",
  "filters": {
    "log_timeframe": "24h",
    "log_level": "error",
    "log_service": "api-gateway"
  }
}
```

---

## 🔍 Troubleshooting

### n8n không connect được MCP:

**Docker → Host:**
```bash
# Thay vì localhost, dùng:
http://host.docker.internal:3001
```

**Network issues:**
```bash
# Check MCP health từ n8n container
docker exec -it n8n curl http://host.docker.internal:3001/health
```

**CORS errors:**
- MCP Server đã có CORS enabled
- Check browser console nếu test qua UI

### Webhook không hoạt động:

**Check webhook URL:**
```bash
# Test trực tiếp
curl -X POST https://n8n-prod.iconiclogs.com/webhook/mcp-check \
  -H 'Content-Type: application/json' \
  -d '{"query": "test"}'
```

**Check n8n logs:**
- n8n → Settings → Log Streaming
- Hoặc: `docker logs n8n`

---

## 📊 Monitor n8n Executions

### Trong n8n UI:
1. **Executions:** Xem history của workflows
2. **Error Workflow:** Setup workflow để handle errors
3. **Logs:** Check execution logs

### Useful n8n Settings:
- **Settings → Error Workflow:** Set workflow để catch all errors
- **Settings → Timezone:** Set đúng timezone
- **Settings → Execution Data:** Save execution data

---

## 🎯 Best Practices

1. **Error Handling:**
   - Always có IF node để check success
   - Setup error notifications
   - Log failed executions

2. **Testing:**
   - Test với Manual Trigger trước
   - Sau đó enable Schedule
   - Monitor executions đầu tiên

3. **Security:**
   - Dùng environment variables cho sensitive data
   - Không hardcode API keys trong workflow
   - Use n8n credentials store

4. **Performance:**
   - Batch requests khi có thể
   - Set reasonable timeouts
   - Monitor execution times

---

## 📚 Resources

- **n8n Docs:** https://docs.n8n.io
- **MCP Server Endpoints:** See [README.md](README.md)
- **Example Workflows:** See `/examples` folder (tạo nếu cần)

---

## ✅ Quick Start Summary

```bash
# 1. Start MCP Server
cd mcp-sse-server-python
./demo-start.sh

# 2. Start n8n (new terminal)
n8n

# 3. Open n8n
open http://localhost:5678

# 4. Create workflow:
# - Manual Trigger
# - HTTP Request → http://localhost:3001/n8n/webhook/demo
# - Body: {"tool": "check_system_abc", "params": {"query": "Check all systems"}}

# 5. Execute!
```

**Done! Bạn đã có n8n workflow hoạt động với MCP Server! 🎉**
