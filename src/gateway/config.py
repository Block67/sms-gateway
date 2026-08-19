from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewayProvider(StrEnum):
    JASMIN = "jasmin"
    LOCAL = "local"


class GatewayConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GATEWAY_PROVIDER: GatewayProvider = GatewayProvider.LOCAL
    JASMIN_BASE_URL: str = "http://localhost:8990"
    JASMIN_USERNAME: str = ""
    JASMIN_PASSWORD: str = ""


gateway_config = GatewayConfig()
