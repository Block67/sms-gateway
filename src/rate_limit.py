from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def get_rate_limit_key(request: Request) -> str:
    """Key by API key so each client gets its own quota. Requests without
    a key (or before auth is checked) fall back to the client IP."""
    api_key = request.headers.get("X-API-Key")
    return api_key if api_key else get_remote_address(request)


limiter = Limiter(key_func=get_rate_limit_key)
