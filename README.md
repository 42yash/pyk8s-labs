docker-compose up --build


From now on, remember this pattern for any database schema changes:

    1. To generate a new migration file: docker-compose exec --user root backend alembic revision --autogenerate -m "Message"

    2. Then fix ownership: sudo chown -R $USER:$USER backend/alembic/

    3. To apply the migration: docker-compose exec backend alembic upgrade head