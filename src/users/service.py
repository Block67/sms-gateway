import secrets
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)


async def get_user_by_api_key(db: AsyncSession, api_key: str) -> User | None:
    return await db.scalar(select(User).where(User.api_key == api_key))


async def create_user(db: AsyncSession, email: str, is_test: bool = False) -> User:
    user = User(email=email, api_key=generate_api_key(), is_test=is_test)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def debit_balance(db: AsyncSession, user: User, amount: Decimal) -> None:
    user.balance = (user.balance or Decimal(0)) - amount
    await db.commit()
