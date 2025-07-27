docker-compose up --build
docker-compose exec backend alembic upgrade head

getent group docker
add number to backend dockerfile

export DOCKER_GID=$(getent group docker | cut -d: -f3)


From now on, remember this pattern for any database schema changes:

    1. To generate a new migration file: docker-compose exec --user root backend alembic revision --autogenerate -m "Message"

    2. Then fix ownership: sudo chown -R $USER:$USER backend/alembic/

    3. To apply the migration: docker-compose exec backend alembic upgrade head