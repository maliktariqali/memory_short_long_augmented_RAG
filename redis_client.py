import redis

from config import REDIS_URL

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)
#decode_responses=True: Tells the client to automatically decode binary Redis 
# responses into UTF-8 Python strings. 
# Without this flag, Redis returns bytes objects (e.g., b'hello' instead of 'hello').
