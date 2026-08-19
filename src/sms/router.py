import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.messages import service as message_service
from src.messages.exceptions import MessageNotFound
from src.messages.schemas import MessageRead
from src.pagination import PaginatedResponse, PaginationParams
from src.rate_limit import limiter
from src.sms import service
from src.sms.schemas import SMSSendRequest
from src.users.dependencies import get_current_user
from src.users.models import User

router = APIRouter(prefix="/sms", tags=["sms"])


@router.post("/send", response_model=MessageRead, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def send_sms(
    request: Request,
    payload: SMSSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.send_sms(db, current_user, payload)


@router.get("", response_model=PaginatedResponse[MessageRead])
async def list_messages(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.list_by_owner(db, current_user.id, pagination)


@router.get("/{message_id}", response_model=MessageRead)
async def get_message_status(
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    message = await message_service.get_owned_message(db, current_user.id, message_id)
    if message is None:
        raise MessageNotFound
    return message
