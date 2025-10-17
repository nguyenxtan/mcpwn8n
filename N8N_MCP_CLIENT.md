# 🔗 n8n MCP Client Integration

Hướng dẫn dùng **n8n MCP Client node** để kết nối trực tiếp với MCP Server

---

## 📋 Prerequisites

- **n8n version:** v1.0.0+
- **MCP Server:** Đang chạy và accessible
- **SSE Support:** MCP Server hỗ trợ SSE (✅ chúng ta có)

---

## ✅ Kiểm tra MCP Server Support

```bash
# Check MCP Server endpoints
curl http://localhost:3001/info | jq

# Check available tools
curl http://localhost:3001/tools | jq
```

Output mong đợi:
```json
{
  "tools": [
    {
      "name": "check_system_abc",
      "description": "...",
      "inputSchema": {...}
    }
  ]
}
```

---

## 🚀 Setup n8n với MCP Client Node

### Bước 1: Check MCP Client Node có sẵn không

**n8n Dashboard:**
1. Tạo workflow mới
2. Click **Add Node** (+)
3. Tìm **"MCP Client"** hoặc **"Model Context Protocol"**

### Bước 2: Nếu chưa có MCP Client Node

**Install n8n MCP node package:**

```bash
# Stop n8n trước
# Ctrl+C

# Cài package
npm install -g @langchain/core n8n-nodes-mcp

# Hoặc qua n8n UI:
# Community Nodes → Search "mcp" → Install

# Restart n8n
n8n
```

---

## 🎯 Tạo Workflow với MCP Client Node

### Workflow 1: Basic System Check

#### Node 1: Manual Trigger
- Tìm: **"Manual Trigger"**
- Để default

#### Node 2: MCP Client
- Tìm: **"MCP Client"** hoặc **"Model Context Protocol"**
- **Credentials/Connection:**
  - **Transport:** SSE (Server-Sent Events)
  - **MCP Server URL:** `http://localhost:3001/sse`
    - Hoặc nếu trên server: `https://mcp.yourdomain.com/sse`

#### Node 3: Initialize MCP
- Add node: **"MCP Client"** (hoặc "Initialize")
- **Connection:** [Select MCP connection]
- **Action:** Initialize
- **Client Info:**
  - **Name:** n8n-client
  - **Version:** 1.0.0

#### Node 4: List Tools
- Add node: **"MCP Client"**
- **Action:** List Tools
- Xem available tools

#### Node 5: Call Tool
- Add node: **"MCP Client"**
- **Action:** Call Tool
- **Tool Name:** `check_system_abc`
- **Arguments:**
```json
{
  "query": "Kiểm tra toàn bộ hệ thống"
}
```

#### Node 6: Process Result
- Add node: **"Set"** (để format output)
- Map fields từ MCP result

---

## 📝 Example: Complete MCP Workflow

```json
{
  "name": "MCP System Check via Client",
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "name": "Initialize MCP",
      "type": "n8n-nodes-mcp.mcp",
      "parameters": {
        "resourceType": "connection",
        "transportType": "sse",
        "mcpServerUrl": "http://localhost:3001/sse"
      },
      "position": [450, 300]
    },
    {
      "name": "Call Tool",
      "type": "n8n-nodes-mcp.mcp",
      "parameters": {
        "action": "callTool",
        "toolName": "check_system_abc",
        "arguments": {
          "query": "Check all systems"
        }
      },
      "position": [650, 300]
    },
    {
      "name": "Process Result",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "success": "{{ $json.success }}",
          "data": "{{ $json.data }}",
          "execution_time": "{{ $json.execution_time_ms }}"
        }
      },
      "position": [850, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Initialize MCP"}]]
    },
    "Initialize MCP": {
      "main": [[{"node": "Call Tool"}]]
    },
    "Call Tool": {
      "main": [[{"node": "Process Result"}]]
    }
  }
}
```

---

## 🔌 MCP Connection Configuration

### SSE (Recommended)
```
Transport: SSE
URL: http://localhost:3001/sse
Heartbeat Interval: 30 (seconds)
Reconnect Timeout: 5 (seconds)
```

### Stdio (Alternative - cho local/dev)
```
Transport: Stdio
Command: python /path/to/src/main.py
```

### WebSocket (If supported)
```
Transport: WebSocket
URL: ws://localhost:3001/ws
```

---

## 🛠️ MCP Client Node Actions

### 1. Initialize
- **Purpose:** Setup connection
- **Output:** Server info, capabilities

### 2. List Tools
- **Purpose:** Get available tools
- **Output:** Array of tools with schemas

### 3. Call Tool
- **Purpose:** Execute tool
- **Input:** Tool name + arguments
- **Output:** Tool result

### 4. Dispose
- **Purpose:** Close connection
- **Output:** None

---

## 📋 Workflow Examples

### Example 1: Auto-check dengan Schedule

```
Schedule Trigger (Daily 9 AM)
  ↓
Initialize MCP
  ↓
Call Tool: check_system_abc (query: "Check all systems")
  ↓
IF (success)
  ├→ Send Slack: ✅ System OK
  └→ Send Slack: ❌ Errors found
```

### Example 2: Interactive Query

```
Manual Trigger (or Webhook)
  ↓
Ask AI (Claude/GPT): "What query to run?"
  ↓
Initialize MCP
  ↓
Call Tool: check_system_abc (query: AI response)
  ↓
Format Result
  ↓
Send Response
```

### Example 3: Continuous Monitoring

```
Trigger Every 5 Minutes
  ↓
Initialize MCP
  ↓
Call Tool: check_system_abc (query: "Check metrics")
  ↓
IF (error_rate > 5%)
  ├→ Send Alert
  └→ Log to Database
  ↓
Call Tool: check_system_abc (query: "Find error logs")
  ↓
IF (errors found)
  ├→ Create Jira ticket
  └→ Notify team
```

---

## 🎯 MCP Client Node Settings

### Connection Tab
```
Connection Type: MCP Server
Transport: SSE
Server URL: http://localhost:3001/sse
Auto-connect: true
Retry on failure: true
Max retries: 3
```

### Action Tab
```
Action: Call Tool
Tool Name: check_system_abc
Arguments (JSON): {
  "query": "Kiểm tra toàn bộ hệ thống"
}
```

### Options Tab
```
Timeout: 30s
Include raw response: true
Error handling: Continue on error
```

---

## 💡 Advanced: Custom Arguments

### Dynamic Query từ Input

```
Node: Manual Trigger
├─ Input: { "query": "Check users" }

Node: MCP Client
├─ Arguments:
   {
     "query": "{{ $input.json.query }}"
   }
```

### Conditional Arguments

```
IF node:
├─ Condition: $json.checkType === "full"
├─ TRUE: call_tool with all APIs
└─ FALSE: call_tool with specific API
```

### With Filters

```json
{
  "query": "Check logs",
  "filters": {
    "log_timeframe": "{{ $json.timeframe || '1h' }}",
    "log_level": "{{ $json.level || 'error' }}"
  }
}
```

---

## 🔍 Troubleshooting

### 1. MCP Client Node không dòng

**Solutions:**
```bash
# A. Check n8n version
n8n --version  # Should be v1.0.0+

# B. Check MCP package
npm list | grep mcp

# C. Reinstall
npm uninstall -g n8n
npm install -g n8n
npm install -g @langchain/core

# D. Restart n8n
# Ctrl+C
n8n
```

### 2. Connection timeout

**Solutions:**
```bash
# A. Check MCP Server chạy
curl http://localhost:3001/health

# B. Check port 3001
netstat -tulpn | grep 3001

# C. Check firewall
sudo ufw status

# D. Tăng timeout trong node
# Timeout: 60s (thay vì 30s)
```

### 3. SSE Connection error

**Solutions:**
```bash
# Test SSE endpoint
curl -N http://localhost:3001/sse

# Check MCP logs
docker logs mcp-sse-server

# Verify SSE support
curl http://localhost:3001/info | jq
```

### 4. Tool không nhận arguments

**Solutions:**
- Check tool schema: `curl http://localhost:3001/tools | jq`
- Verify argument format matches schema
- Use "Include raw response" để debug

---

## 📊 Monitoring MCP Connections

### n8n UI
- **Executions:** View workflow runs
- **Debug:** See MCP client logs
- **Credentials:** Manage MCP connections

### MCP Server
```bash
# View logs
docker logs -f mcp-sse-server

# Check active connections
curl http://localhost:3001/connections

# Check metrics
curl http://localhost:3001/metrics
```

---

## 🎨 Best Practices

### 1. Connection Management
```
Initialize MCP
  ↓
Do work
  ↓
Dispose MCP (Cleanup)
```

### 2. Error Handling
```
Call Tool
  ↓
IF Success
├→ Process result
└→ Handle error
  ↓
Dispose MCP
```

### 3. Performance
- Reuse connection nếu có thể
- Batch multiple tool calls
- Set reasonable timeouts

### 4. Security
- Không hardcode sensitive data
- Use n8n credentials store
- Validate inputs

---

## 📚 Resources

- **n8n MCP Docs:** https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-langchain/n8n-nodes-langchain-mcp/
- **MCP Spec:** https://modelcontextprotocol.io
- **n8n Docs:** https://docs.n8n.io

---

## ✅ Quick Start

```
1. Open n8n: http://localhost:5678

2. Create workflow:
   - Manual Trigger
   - MCP Client (Initialize)
   - MCP Client (Call Tool)
   - Set (Process)

3. Configure MCP Client:
   - URL: http://localhost:3001/sse
   - Tool: check_system_abc
   - Query: "Check all systems"

4. Execute!

5. View result
```

---

**That's it! n8n MCP Client setup ready! 🚀**
