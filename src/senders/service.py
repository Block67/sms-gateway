import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.senders.constants import SenderStatus
from src.senders.exceptions import InvalidSenderId, SenderAlreadyExists, SenderNotFound
from src.senders.models import Sender
from src.senders.schemas import SenderCreate
from src.users.models import User

DEFAULT_TEST_SENDER = "TESTSENDER"


async def create_sender(db: AsyncSession, owner_id: uuid.UUID, sender_in: SenderCreate) -> Sender:
    existing = await db.scalar(
        select(Sender).where(Sender.owner_id == owner_id, Sender.name == sender_in.name)
    )
    if existing is not None:
        raise SenderAlreadyExists

    sender = Sender(owner_id=owner_id, name=sender_in.name, status=SenderStatus.PENDING)
    db.add(sender)
    await db.commit()
    await db.refresh(sender)
    return sender


async def list_senders(db: AsyncSession, owner_id: uuid.UUID) -> list[Sender]:
    result = await db.execute(select(Sender).where(Sender.owner_id == owner_id))
    return list(result.scalars().all())


async def get_sender_or_404(db: AsyncSession, sender_id: uuid.UUID) -> Sender:
    sender = await db.get(Sender, sender_id)
    if sender is None:
        raise SenderNotFound
    return sender


async def approve_sender(db: AsyncSession, sender: Sender, admin_id: uuid.UUID) -> Sender:
    sender.status = SenderStatus.ACTIVE
    sender.approved_by = admin_id
    sender.approved_at = datetime.now(UTC)
    sender.rejection_reason = None
    await db.commit()
    await db.refresh(sender)
    return sender


async def reject_sender(db: AsyncSession, sender: Sender, reason: str | None) -> Sender:
    sender.status = SenderStatus.REJECTED
    sender.rejection_reason = reason
    await db.commit()
    await db.refresh(sender)
    return sender


async def check_sender(db: AsyncSession, user: User, name: str | None) -> str:
    """Equivalent du `checkSender` Node : un sender n'est utilisable que par
    son propriétaire (owner_id = user.id), et seulement s'il est ACTIVE."""
    if not name and user.is_test:
        return DEFAULT_TEST_SENDER

    if not name:
        raise InvalidSenderId(detail="Sender ID is required")

    sender = await db.scalar(
        select(Sender).where(
            Sender.owner_id == user.id,
            Sender.name == name,
            Sender.status == SenderStatus.ACTIVE,
        )
    )
    if sender is None:
        raise InvalidSenderId

    return sender.name
