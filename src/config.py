from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

    @property
    def is_debug(self) -> bool:
        return self in (self.LOCAL, self.STAGING, self.TESTING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: Environment = Environment.LOCAL
    DATABASE_URL: str = "postgresql+asyncpg://sms_user:sms_password@localhost:5432/sms_gateway"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    RATE_LIMIT_PER_MINUTE: int = 300


settings = Settings()
