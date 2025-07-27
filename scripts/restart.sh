#!/bin/bash

# A "smart" restart script for the development environment.
# It only rebuilds containers if their dependencies have changed.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 1. Stop Running Containers ---
echo "🛑 Stopping all services..."
docker-compose down
echo "✅ Services stopped."
echo

# --- 2. Build Only What's Necessary ---
# The 'build' command is smart. It uses Docker's cache and will only
# rebuild an image if its Dockerfile or the files it copies (like requirements.txt
# or package.json) have changed.
echo "🚀 Building services (will use cache if possible)..."
docker-compose build
echo "✅ Build step complete."
echo

# --- 3. Start All Services ---
echo "⬆️ Starting all services in detached mode..."
docker-compose up -d
echo "✅ Services started."
echo

# --- 4. Apply Database Migrations ---
echo "Applying database migrations..."
# Add a small delay for the database to initialize fully.
sleep 5

# Retry loop to robustly handle the DB not being ready immediately.
for i in {1..5}; do
    # Check if the backend container is running before trying to exec
    if [ "$(docker-compose ps -q backend)" ] && [ "$(docker-compose ps -q backend | xargs docker inspect -f '{{.State.Running}}')" == "true" ]; then
        echo "Attempting to apply migrations (try $i)..."
        docker-compose exec backend alembic upgrade head && break
    fi
    echo "Database or backend not ready yet, retrying in 3 seconds..."
    sleep 3
done

echo
echo "🎉 Development environment restarted! Your application is ready at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend Docs: http://localhost:8000/docs"