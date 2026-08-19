from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.config import settings
from src.dlr.router import router as dlr_router
from src.operators.router import router as operators_router
from src.pricing.router import router as pricing_router
from src.rate_limit import limiter
from src.senders.router import router as senders_router
from src.sms.router import router as sms_router
from src.users.router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="fastapi-sms-gateway")

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users_router)
    app.include_router(senders_router)
    app.include_router(operators_router)
    app.include_router(pricing_router)
    app.include_router(sms_router)
    app.include_router(dlr_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
