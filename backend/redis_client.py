# backend/redis_client.py
import redis.asyncio as redis
from core.config import settings

# Create a connection pool for Redis
# The 'decode_responses=True' is important so we get strings back from Redis, not bytes.
redis_pool = redis.ConnectionPool.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    decode_responses=True
)

def get_redis_connection():
    """Returns a Redis connection from the pool."""
    return redis.Redis(connection_pool=redis_pool)