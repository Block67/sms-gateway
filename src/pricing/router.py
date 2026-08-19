from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.pricing import service
from src.pricing.models import UserPrice
from src.pricing.schemas import UserPriceRead, UserPriceSet
from src.users.dependencies import get_current_admin
from src.users.models import User

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post("", response_model=UserPriceRead, status_code=status.HTTP_201_CREATED)
async def set_price(
    payload: UserPriceSet,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UserPrice:
    return await service.set_price(db, payload)
