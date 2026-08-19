from functools import lru_cache

from src.gateway.base import SMSGateway
from src.gateway.config import GatewayProvider, gateway_config
from src.gateway.jasmin import JasminGateway
from src.gateway.local import LocalGateway


@lru_cache
def get_gateway() -> SMSGateway:
    if gateway_config.GATEWAY_PROVIDER == GatewayProvider.JASMIN:
        return JasminGateway()
    return LocalGateway()
