#!/bin/bash

# Creative Campaign - Start Script
# Starts the infrastructure and API services

set -e

echo "══════════════════════════════════════════════════════════"
echo "  🚀 Starting Creative Campaign Infrastructure"
echo "══════════════════════════════════════════════════════════"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to edit .env first..."
fi

# Start infrastructure services
echo "📦 Starting MongoDB, NATS, MinIO, Portainer..."
docker-compose up -d mongodb nats minio minio-init portainer

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Wait for MongoDB
echo "  Checking MongoDB..."
until docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo "    MongoDB not ready yet..."
    sleep 2
done
echo "  ✅ MongoDB is ready"

# Wait for NATS
echo "  Checking NATS..."
until curl -sf http://localhost:8222/healthz > /dev/null 2>&1; do
    echo "    NATS not ready yet..."
    sleep 2
done
echo "  ✅ NATS is ready"

# Wait for MinIO
echo "  Checking MinIO..."
until curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    echo "    MinIO not ready yet..."
    sleep 2
done
echo "  ✅ MinIO is ready"

echo ""
echo "🔨 Building and starting API Gateway..."
DOCKER_BUILDKIT=0 docker-compose up -d --build api

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  ✅ Creative Campaign is running!"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "📊 Services:"
echo "  • API Gateway:    http://localhost:8000"
echo "  • API Docs:       http://localhost:8000/docs"
echo "  • API Metrics:    http://localhost:8000/metrics"
echo "  • MongoDB:        mongodb://localhost:27017"
echo "  • NATS:           nats://localhost:4222"
echo "  • NATS Monitor:   http://localhost:8222"
echo "  • MinIO Console:  http://localhost:9001 (minioadmin/minioadmin)"
echo "  • Portainer UI:   http://localhost:9000"
echo ""
echo "🔍 View logs:"
echo "  docker-compose logs -f api"
echo ""
echo "🛑 Stop services:"
echo "  ./stop.sh"
echo ""
