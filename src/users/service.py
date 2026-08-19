import secrets
from decimal import Decimal

from sqlalchemy import select, update
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


async def debit_balance(db: AsyncSession, user: User, amount: Decimal) -> bool:
    """Atomic conditional debit: the balance check and the deduction happen
    in a single UPDATE, so concurrent requests for the same user can't both
    read the same starting balance and overdraw it (lost update)."""
    result = await db.execute(
        update(User)
        .where(User.id == user.id, User.balance >= amount)
        .values(balance=User.balance - amount)
        .returning(User.balance)
    )
    new_balance = result.scalar_one_or_none()
    if new_balance is None:
        await db.rollback()
        return False

    user.balance = new_balance
    await db.commit()
    return True
