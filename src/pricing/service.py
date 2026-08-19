import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.pricing.exceptions import PriceNotDefined
from src.pricing.models import UserPrice
from src.pricing.schemas import UserPriceSet


async def get_price(db: AsyncSession, user_id: uuid.UUID, operator_id: uuid.UUID) -> Decimal:
    price = await db.scalar(
        select(UserPrice.price).where(
            UserPrice.user_id == user_id, UserPrice.operator_id == operator_id
        )
    )
    if price is None:
        raise PriceNotDefined
    return price


async def set_price(db: AsyncSession, payload: UserPriceSet) -> UserPrice:
    existing = await db.scalar(
        select(UserPrice).where(
            UserPrice.user_id == payload.user_id, UserPrice.operator_id == payload.operator_id
        )
    )
    if existing is not None:
        existing.price = payload.price
        await db.commit()
        await db.refresh(existing)
        return existing

    user_price = UserPrice(**payload.model_dump())
    db.add(user_price)
    await db.commit()
    await db.refresh(user_price)
    return user_price
