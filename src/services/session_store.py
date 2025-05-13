import redis
import json
from src.config import AppConfig


class RedisSessionStore:
    def __init__(self):
        self.client = redis.Redis(
            host=AppConfig.REDIS.HOST,
            port=AppConfig.REDIS.PORT,
            db=AppConfig.REDIS.DB,
            password=AppConfig.REDIS.PASSWORD,
            decode_responses=True
        )
        self.ttl = AppConfig.REDIS.TTL_SECONDS

    def set_session(self, user_id: str, chat_state: dict):
        try:
            self.client.set(f"chat:{user_id}", json.dumps(chat_state), ex=self.ttl)
        except redis.RedisError as e:
            raise RuntimeError(f"Failed to set Redis session: {e}")

    def get_session(self, user_id: str) -> dict | None:
        try:
            raw = self.client.get(f"chat:{user_id}")
            data = json.loads(raw) if raw else None
            return data if isinstance(data, list) else None
        except redis.RedisError as e:
            raise RuntimeError(f"Failed to get Redis session: {e}")
        except json.JSONDecodeError:
            return None

    def delete_session(self, user_id: str):
        try:
            self.client.delete(f"chat:{user_id}")
        except redis.RedisError as e:
            raise RuntimeError(f"Failed to delete Redis session: {e}")
