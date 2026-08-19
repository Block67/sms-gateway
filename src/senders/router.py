import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.senders import service
from src.senders.models import Sender
from src.senders.schemas import SenderCreate, SenderRead, SenderReject
from src.users.dependencies import get_current_admin, get_current_user
from src.users.models import User

router = APIRouter(prefix="/senders", tags=["senders"])


@router.post("", response_model=SenderRead, status_code=status.HTTP_201_CREATED)
async def register_sender(
    sender_in: SenderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sender:
    return await service.create_sender(db, current_user.id, sender_in)


@router.get("", response_model=list[SenderRead])
async def list_my_senders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Sender]:
    return await service.list_senders(db, current_user.id)


@router.patch("/{sender_id}/approve", response_model=SenderRead)
async def approve_sender(
    sender_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> Sender:
    sender = await service.get_sender_or_404(db, sender_id)
    return await service.approve_sender(db, sender, admin.id)


@router.patch("/{sender_id}/reject", response_model=SenderRead)
async def reject_sender(
    sender_id: uuid.UUID,
    payload: SenderReject,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> Sender:
    sender = await service.get_sender_or_404(db, sender_id)
    return await service.reject_sender(db, sender, payload.reason)
