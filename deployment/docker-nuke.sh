#!/bin/bash
# ============================================================================
# Docker Nuclear Option - Destroy EVERYTHING
# ============================================================================
# WARNING: This script will DELETE ALL Docker resources on your system:
# - All running and stopped containers
# - All images
# - All volumes
# - All networks (except default)
# - All build cache
# - Everything!
# ============================================================================

set -e

echo "☢️  DOCKER NUCLEAR OPTION ☢️"
echo ""
echo "⚠️  WARNING: This will PERMANENTLY DELETE:"
echo "   • All containers (running and stopped)"
echo "   • All images"
echo "   • All volumes"
echo "   • All custom networks"
echo "   • All build cache"
echo "   • Everything else Docker-related"
echo ""
echo "This action CANNOT be undone!"
echo ""

# Prompt for confirmation
read -p "Are you absolutely sure? Type 'YES' to continue: " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo "❌ Aborted. Nothing was deleted."
    exit 0
fi

echo ""
echo "🔥 Starting Docker annihilation..."
echo ""

# Stop all running containers
echo "🛑 Stopping all running containers..."
if [ "$(docker ps -q)" ]; then
    docker stop $(docker ps -q)
    echo "   ✅ All containers stopped"
else
    echo "   ℹ️  No running containers"
fi
echo ""

# Remove all containers
echo "🗑️  Removing all containers..."
if [ "$(docker ps -aq)" ]; then
    docker rm -f $(docker ps -aq)
    echo "   ✅ All containers removed"
else
    echo "   ℹ️  No containers to remove"
fi
echo ""

# Remove all images
echo "🗑️  Removing all images..."
if [ "$(docker images -q)" ]; then
    docker rmi -f $(docker images -q)
    echo "   ✅ All images removed"
else
    echo "   ℹ️  No images to remove"
fi
echo ""

# Remove all volumes
echo "🗑️  Removing all volumes..."
if [ "$(docker volume ls -q)" ]; then
    docker volume rm -f $(docker volume ls -q) 2>/dev/null || docker volume prune -f
    echo "   ✅ All volumes removed"
else
    echo "   ℹ️  No volumes to remove"
fi
echo ""

# Remove all custom networks
echo "🗑️  Removing all custom networks..."
if [ "$(docker network ls -q -f type=custom)" ]; then
    docker network ls -q -f type=custom | xargs -r docker network rm 2>/dev/null || true
    echo "   ✅ All custom networks removed"
else
    echo "   ℹ️  No custom networks to remove"
fi
echo ""

# Remove all build cache
echo "🗑️  Removing all build cache..."
docker builder prune -af
echo "   ✅ Build cache cleared"
echo ""

# Final system prune (catch anything remaining)
echo "🧹 Final cleanup - removing all unused data..."
docker system prune -af --volumes
echo "   ✅ System pruned"
echo ""

# Show remaining Docker disk usage
echo "📊 Remaining Docker disk usage:"
docker system df
echo ""

echo "✅ Docker annihilation complete!"
echo "   All Docker resources have been destroyed."
echo ""
