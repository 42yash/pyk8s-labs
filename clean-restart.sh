#!/bin/bash

# A script to perform a "nuke and pave" reset of the Docker development environment.
# This is useful when dependencies are out of sync or volumes are causing issues.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 1. Stop and Remove All Containers, Networks, and Volumes ---
echo "🛑 Stopping and removing all containers, networks, and volumes..."
docker-compose down -v
echo "✅ Docker environment completely stopped and cleared."
echo

# --- 2. Prune Docker System Cache (Optional but Recommended) ---
# This is an aggressive cleanup of any dangling images and build caches.
echo "🧹 Pruning Docker system cache..."
docker system prune -af --volumes
echo "✅ Docker system cache pruned."
echo

# --- 3. Clean Frontend Artifacts ---
echo "🧹 Cleaning frontend build artifacts and dependencies..."
if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    echo "🗑️  Deleted frontend/.next cache."
fi
if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    echo "🗑️  Deleted frontend/node_modules."
fi
if [ -f "frontend/package-lock.json" ]; then
    rm -f frontend/package-lock.json
    echo "🗑️  Deleted frontend/package-lock.json."
fi
echo "✅ Frontend directory cleaned."
echo

# --- 4. (Optional) Restart Docker Engine ---
# Uncomment the block below for your specific OS if you suspect deep issues
# with the Docker daemon itself.

# For macOS (with Docker Desktop):
# echo "⏳ Restarting Docker Desktop (macOS)..."
# osascript -e 'quit app "Docker"'
# open --background -a Docker
# echo "⏰ Waiting for Docker daemon to be ready..."
# while ! docker system info > /dev/null 2>&1; do
#   sleep 1
# done
# echo "✅ Docker Desktop restarted."
# echo

# For Linux (systemd):
# echo "⏳ Restarting Docker service (Linux)..."
# sudo systemctl restart docker
# echo "✅ Docker service restarted."
# echo

# --- 5. Rebuild and Start Fresh ---
echo "🚀 Building and starting all services from scratch..."
docker-compose up --build -d
echo
echo "✅ All services have been rebuilt and started in detached mode."
echo

# --- 6. Apply Database Migrations ---
echo "Applying database migrations..."
# It can take a few seconds for the database to be ready.
# We'll add a small delay and a retry loop to be robust.
for i in {1..5}; do
    # The `|| true` prevents the script from exiting if the DB isn't ready yet
    docker-compose exec backend alembic upgrade head && break || true
    echo "Database not ready yet, retrying in 3 seconds..."
    sleep 3
done

echo
echo "🎉 Environment reset complete! Your application is ready at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend Docs: http://localhost:8000/docs"