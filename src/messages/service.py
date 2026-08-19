import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.messages.constants import MessageStatus
from src.messages.models import Message
from src.pagination import PaginatedResponse, PaginationParams


async def create_message(
    db: AsyncSession,
    *,
    owner_id: uuid.UUID,
    sender_name: str,
    to_number: str,
    text: str,
    price: Decimal,
    pages: int,
    operator_id: uuid.UUID,
    dlr_url: str | None,
) -> Message:
    message = Message(
        owner_id=owner_id,
        sender_name=sender_name,
        to_number=to_number,
        text=text,
        price=price,
        pages=pages,
        operator_id=operator_id,
        dlr_url=dlr_url,
        status=MessageStatus.QUEUED,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_by_id(db: AsyncSession, message_id: uuid.UUID) -> Message | None:
    return await db.get(Message, message_id)


async def get_owned_message(db: AsyncSession, owner_id: uuid.UUID, message_id: uuid.UUID) -> Message | None:
    message = await db.get(Message, message_id)
    if message is None or message.owner_id != owner_id:
        return None
    return message


async def get_by_provider_message_id(db: AsyncSession, provider_message_id: str) -> Message | None:
    return await db.scalar(select(Message).where(Message.provider_message_id == provider_message_id))


async def update_status(
    db: AsyncSession,
    message: Message,
    *,
    status: MessageStatus,
    provider_message_id: str | None = None,
    error: str | None = None,
    delivered_at: datetime | None = None,
) -> Message:
    message.status = status
    if provider_message_id is not None:
        message.provider_message_id = provider_message_id
    if error is not None:
        message.error = error
    if delivered_at is not None:
        message.delivered_at = delivered_at
    await db.commit()
    await db.refresh(message)
    return message


async def list_by_owner(
    db: AsyncSession, owner_id: uuid.UUID, pagination: PaginationParams
) -> PaginatedResponse[Message]:
    base_query = select(Message).where(Message.owner_id == owner_id)

    total = await db.scalar(select(func.count()).select_from(base_query.subquery()))

    result = await db.execute(
        base_query.order_by(Message.created_at.desc()).limit(pagination.limit).offset(pagination.offset)
    )
    items = list(result.scalars().all())

    return PaginatedResponse(items=items, total=total or 0, limit=pagination.limit, offset=pagination.offset)
