from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    # Database
    DATABASE_URL: str = "postgresql://statsentry:password@localhost:5432/statsentry"
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Keys - Set defaults for development, override in production
    STEAM_API_KEY: str = "your-steam-api-key-here"
    LEETIFY_API_KEY: Optional[str] = None

    # Security - Set defaults for development, override in production
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Steam OAuth
    STEAM_OPENID_URL: str = "https://steamcommunity.com/openid"
    FRONTEND_URL: str = "http://localhost:3000"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Development
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()