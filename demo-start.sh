#!/bin/bash

# Demo Start Script - Quick launch MCP Server với Mock API

set -e

echo "================================================"
echo "   MCP SSE Server - DEMO MODE"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found!"
    echo "Please install docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ docker-compose is available"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
echo ""

# Build and start services
echo "🚀 Starting services..."
echo "   - Mock API Server (port 8000)"
echo "   - MCP SSE Server (port 3001)"
echo "   - Prometheus (port 9090)"
echo "   - Grafana (port 3000)"
echo ""

docker-compose -f docker-compose.dev.yml up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "🔍 Checking service health..."
echo ""

# Check Mock API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Mock API is healthy (http://localhost:8000)"
else
    echo "⚠️  Mock API not responding yet..."
fi

# Check MCP Server
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✅ MCP Server is healthy (http://localhost:3001)"
else
    echo "⚠️  MCP Server not responding yet..."
fi

echo ""
echo "================================================"
echo "   DEMO READY! 🎉"
echo "================================================"
echo ""
echo "📊 Services:"
echo "   Mock API:    http://localhost:8000"
echo "   MCP Server:  http://localhost:3001"
echo "   Prometheus:  http://localhost:9090"
echo "   Grafana:     http://localhost:3000 (admin/admin)"
echo ""
echo "📖 Quick Tests:"
echo ""
echo "   # Test Mock API"
echo "   curl http://localhost:8000/api/system/health | jq"
echo ""
echo "   # Test MCP Server"
echo "   curl http://localhost:3001/info | jq"
echo ""
echo "   # Test System Check (Vietnamese)"
echo "   curl -X POST http://localhost:3001/n8n/webhook/demo \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"tool\": \"check_system_abc\", \"params\": {\"query\": \"Kiểm tra toàn bộ hệ thống\"}}' | jq"
echo ""
echo "   # Test System Check (English)"
echo "   curl -X POST http://localhost:3001/n8n/webhook/demo \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"tool\": \"check_system_abc\", \"params\": {\"query\": \"Check all systems\"}}' | jq"
echo ""
echo "   # Test SSE connection"
echo "   curl -N http://localhost:3001/sse"
echo ""
echo "📚 Full documentation:"
echo "   - See DEMO.md for detailed examples"
echo "   - See README.md for full documentation"
echo ""
echo "🛑 To stop:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""
echo "📋 View logs:"
echo "   docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "================================================"
