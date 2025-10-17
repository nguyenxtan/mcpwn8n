#!/bin/bash

# Test Script - Automated testing cho demo

set -e

BASE_URL="http://localhost:3001"
MOCK_URL="http://localhost:8000"

echo "================================================"
echo "   MCP SSE Server - DEMO TESTS"
echo "================================================"
echo ""

# Function to run test
run_test() {
    local test_name=$1
    local command=$2

    echo "🧪 Testing: $test_name"
    echo "   Command: $command"

    if eval "$command" > /dev/null 2>&1; then
        echo "   ✅ PASS"
    else
        echo "   ❌ FAIL"
    fi
    echo ""
}

# Check if services are running
echo "🔍 Checking if services are running..."
echo ""

if ! curl -s $MOCK_URL/health > /dev/null; then
    echo "❌ Mock API is not running!"
    echo "Run: ./demo-start.sh first"
    exit 1
fi

if ! curl -s $BASE_URL/health > /dev/null; then
    echo "❌ MCP Server is not running!"
    echo "Run: ./demo-start.sh first"
    exit 1
fi

echo "✅ All services are running"
echo ""
echo "================================================"
echo "   Running Tests..."
echo "================================================"
echo ""

# Test 1: Mock API Health
run_test "Mock API - Health Check" \
    "curl -s $MOCK_URL/api/system/health | jq -e '.status'"

# Test 2: Mock API Users
run_test "Mock API - User Status" \
    "curl -s $MOCK_URL/api/users/status | jq -e '.users | length > 0'"

# Test 3: Mock API Services
run_test "Mock API - Services List" \
    "curl -s $MOCK_URL/api/services/list | jq -e '.services | length > 0'"

# Test 4: Mock API Metrics
run_test "Mock API - Current Metrics" \
    "curl -s $MOCK_URL/api/metrics/current | jq -e '.cpu_usage'"

# Test 5: Mock API Logs
run_test "Mock API - Query Logs" \
    "curl -s -X POST $MOCK_URL/api/logs/query -H 'Content-Type: application/json' -d '{\"timeframe\": \"1h\"}' | jq -e '.logs | length > 0'"

echo "================================================"
echo ""

# Test 6: MCP Server Info
run_test "MCP Server - Server Info" \
    "curl -s $BASE_URL/info | jq -e '.server.name'"

# Test 7: MCP Server Tools
run_test "MCP Server - List Tools" \
    "curl -s $BASE_URL/tools | jq -e '.tools | length > 0'"

# Test 8: MCP Server Health
run_test "MCP Server - Health Check" \
    "curl -s $BASE_URL/health | jq -e '.status == \"healthy\"'"

echo "================================================"
echo ""

# Test 9: n8n Webhook - Vietnamese
echo "🧪 Testing: n8n Webhook - Vietnamese Query"
response=$(curl -s -X POST $BASE_URL/n8n/webhook/demo \
    -H 'Content-Type: application/json' \
    -d '{"tool": "check_system_abc", "params": {"query": "Kiểm tra toàn bộ hệ thống"}}')

if echo "$response" | jq -e '.success == true' > /dev/null; then
    echo "   ✅ PASS"
    echo "   Response preview:"
    echo "$response" | jq '.summary' 2>/dev/null || echo "$response" | jq -C '.'
else
    echo "   ❌ FAIL"
    echo "   Response: $response"
fi
echo ""

# Test 10: n8n Webhook - English
echo "🧪 Testing: n8n Webhook - English Query"
response=$(curl -s -X POST $BASE_URL/n8n/webhook/demo \
    -H 'Content-Type: application/json' \
    -d '{"tool": "check_system_abc", "params": {"query": "Check all systems"}}')

if echo "$response" | jq -e '.success == true' > /dev/null; then
    echo "   ✅ PASS"
    echo "   Response preview:"
    echo "$response" | jq '.summary' 2>/dev/null || echo "$response" | jq -C '.'
else
    echo "   ❌ FAIL"
    echo "   Response: $response"
fi
echo ""

# Test 11: Natural Language - Logs query
echo "🧪 Testing: Natural Language - Logs Query"
response=$(curl -s -X POST $BASE_URL/n8n/webhook/demo \
    -H 'Content-Type: application/json' \
    -d '{"tool": "check_system_abc", "params": {"query": "Xem logs 1 giờ gần đây"}}')

if echo "$response" | jq -e '.data.logs' > /dev/null; then
    echo "   ✅ PASS"
    echo "   Found $(echo "$response" | jq '.data.logs.total') logs"
else
    echo "   ❌ FAIL"
fi
echo ""

# Test 12: Natural Language - Metrics query
echo "🧪 Testing: Natural Language - Metrics Query"
response=$(curl -s -X POST $BASE_URL/n8n/webhook/demo \
    -H 'Content-Type: application/json' \
    -d '{"tool": "check_system_abc", "params": {"query": "Get current metrics"}}')

if echo "$response" | jq -e '.data.metrics' > /dev/null; then
    echo "   ✅ PASS"
    echo "   CPU Usage: $(echo "$response" | jq '.data.metrics.cpu_usage')%"
    echo "   Memory Usage: $(echo "$response" | jq '.data.metrics.memory_usage')%"
else
    echo "   ❌ FAIL"
fi
echo ""

echo "================================================"
echo "   TEST SUMMARY"
echo "================================================"
echo ""
echo "✅ All tests completed!"
echo ""
echo "📊 Additional checks:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000"
echo ""
echo "🔍 For detailed testing, see DEMO.md"
echo "================================================"
