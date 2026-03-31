"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
    firebase_service_account: str = ""
    rate_limit: str = "60/minute"
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
