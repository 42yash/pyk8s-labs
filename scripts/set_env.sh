#!/bin/bash

echo "Checking docker group..."
DOCKER_GID=$(getent group docker | cut -d: -f3)
echo "Docker GID: '$DOCKER_GID'"

echo "Getting current user ID..."
UUID=$(id -u)
echo "User ID: '$UUID'"

echo "Current directory: $(pwd)"

echo "Creating .env file..."
cat <<EOL > .env
DOCKER_GID=$DOCKER_GID
UID=$UUID
EOL

if [ $? -eq 0 ]; then
    echo ".env file created successfully."
    echo "Contents:"
    cat .env
else
    echo "Failed to create .env file"
fi
