#!/bin/bash
echo "🛑 Stopping Creative Campaign services..."
docker-compose down
echo "✅ All services stopped"


## 1. Stop and remove containers
#docker stop $(docker ps -aq)
#docker rm $(docker ps -aq)
#
## 2. Remove images
#docker rmi $(docker images -q) -f
#
## 3. Remove volumes (⚠️ this deletes data!)
#docker volume rm $(docker volume ls -q)
#
## 4. Clean everything else
#docker system prune -a --volumes -f