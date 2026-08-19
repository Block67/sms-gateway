import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.messages import service as message_service
from src.messages.constants import MessageStatus
from src.queue.config import queue_config
from src.queue.publisher import publish_dlr_forward_task

logger = logging.getLogger("sms.dlr")

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

    payload = {
        "dlr_url": message.dlr_url,
        "message_id": str(message.id),
        "status": new_status.value,
        "to": message.to_number,
    }
    try:
        await publish_dlr_forward_task(payload)
    except Exception:
        # La queue est indisponible : on retombe sur un envoi synchrone
        # immédiat, même filet de sécurité que le fallback de send_sms.
        await forward_dlr(payload)


async def forward_dlr(payload: dict[str, Any]) -> None:
    """POST le statut au dlr_url du client, avec retry + backoff. Utilisé
    par le worker DLR et par le fallback synchrone de handle_dlr."""
    dlr_url = payload["dlr_url"]
    body = {"message_id": payload["message_id"], "status": payload["status"], "to": payload["to"]}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(1, queue_config.DLR_FORWARD_MAX_RETRIES + 1):
            try:
                await client.post(dlr_url, json=body)
                return
            except httpx.HTTPError as exc:
                if attempt == queue_config.DLR_FORWARD_MAX_RETRIES:
                    logger.warning("Échec transmission DLR %s vers %s après %d tentatives: %s",
                                    body["message_id"], dlr_url, attempt, exc)
                    return
                await asyncio.sleep(queue_config.DLR_FORWARD_RETRY_BACKOFF_SECONDS * attempt)
