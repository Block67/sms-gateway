from fastapi import Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.exceptions import PermissionDenied
from src.users.exceptions import InvalidApiKey
from src.users.models import User
from src.users.service import get_user_by_api_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not api_key:
        raise InvalidApiKey

    user = await get_user_by_api_key(db, api_key)
    if user is None or not user.is_active:
        raise InvalidApiKey

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise PermissionDenied

    return current_user
