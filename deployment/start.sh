#!/bin/bash

# Creative Campaign - Start Script
# Usage: ./start.sh [--build]

set -e

echo "🚀 Starting Creative Campaign..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to edit .env first..."
fi

# Create data directories if they don't exist
echo "📁 Checking data directories..."
mkdir -p data/mongodb data/nats data/minio data/portainer
echo "✅ Data directories ready"
echo ""

# Check for --build flag
if [ "$1" = "--build" ]; then
    echo "🔨 Building all services without cache..."
    docker-compose build --no-cache
    echo "🚀 Starting all services..."
    docker-compose up -d
else
    echo "📦 Starting all services..."
    docker-compose up -d
fi

echo ""
echo "✅ Creative Campaign is running!"
echo ""
echo "📊 Services:"
echo "  • Web UI:         http://localhost:8501"
echo "  • API:            http://localhost:8000"
echo "  • API Docs:       http://localhost:8000/docs"
echo ""
echo "🔍 View logs:      docker-compose logs -f"
echo "🛑 Stop services:  docker-compose down"
echo ""
