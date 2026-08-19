from datetime import UTC, datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.messages import service as message_service
from src.messages.constants import MessageStatus

_STATUS_MAP = {
    "DELIVERED": MessageStatus.DELIVERED,
    "ESME_ROK": MessageStatus.DELIVERED,
    "UNDELIVERED": MessageStatus.UNDELIVERED,
    "EXPIRED": MessageStatus.UNDELIVERED,
    "REJECTED": MessageStatus.REJECTED,
}


async def handle_dlr(db: AsyncSession, provider_message_id: str, raw_status: str, error: str | None) -> None:
    message = await message_service.get_by_provider_message_id(db, provider_message_id)
    if message is None:
        return

    new_status = _STATUS_MAP.get(raw_status.upper(), MessageStatus.UNDELIVERED)
    delivered_at = datetime.now(UTC) if new_status == MessageStatus.DELIVERED else None

    await message_service.update_status(db, message, status=new_status, error=error, delivered_at=delivered_at)

    if not message.dlr_url:
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(
                message.dlr_url,
                json={"message_id": str(message.id), "status": new_status.value, "to": message.to_number},
            )
        except httpx.HTTPError:
            pass
