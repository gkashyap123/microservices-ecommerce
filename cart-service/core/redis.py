import redis
from core.config import settings

# Single Redis client — reused across all requests
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,      # returns str instead of bytes
)

def get_redis() -> redis.Redis:
    return redis_client