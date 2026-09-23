import json

from config import (
    MAX_RECENT_MESSAGES,
    SHORT_TERM_TTL_SECONDS,
)
from redis_client import redis_client

class ShortTermMemory:
    """
    Session-level memory backed by Redis.

    Each session is a capped Redis List (newest at the tail),
    trimmed to max_messages, with a TTL so idle sessions expire.
    """

    def __init__(
        self,
        max_messages=MAX_RECENT_MESSAGES,
        ttl_seconds=SHORT_TERM_TTL_SECONDS,
        client=redis_client,
    ):
        self.max_messages = max_messages
        self.ttl_seconds = ttl_seconds
        self.client = client

    def _key(self, session_key: str) -> str:
        return f"stm:{session_key}"

    def add_message(self, session_key: str, role: str, content: str):
        key = self._key(session_key)
        payload = json.dumps({"role": role, "content": content})

        pipeline = self.client.pipeline()
        pipeline.rpush(key, payload)
        pipeline.ltrim(key, -self.max_messages, -1)
        pipeline.expire(key, self.ttl_seconds)
        pipeline.execute()

    def get_messages(self, session_key: str):
        raw_messages = self.client.lrange(self._key(session_key), 0, -1)
        return [json.loads(item) for item in raw_messages]

    def clear(self, session_key: str):
        self.client.delete(self._key(session_key))

short_term_memory = ShortTermMemory()
