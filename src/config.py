import os

class GeminiConfig:
    MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro-exp-03-25")
    API_KEY = os.getenv("GEMINI_API_KEY")


class RedisConfig:
    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = int(os.getenv("REDIS_PORT", 6379))
    DB = int(os.getenv("REDIS_DB", 0))
    PASSWORD = os.getenv("REDIS_PASSWORD", None)
    TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS", 3600))


class AppConfig:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"
    GEMINI = GeminiConfig
    REDIS = RedisConfig
