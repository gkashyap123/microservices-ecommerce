import redis
from core.config import settings

# Single Redis client — reused across all requests
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,      # returns str instead of bytes
)

def get_redis() -> redis.Redis:
    return redis_client