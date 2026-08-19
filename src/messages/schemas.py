import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.messages.constants import MessageStatus


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: MessageStatus
    to_number: str
    sender_name: str
    price: Decimal
    pages: int
    provider_message_id: str | None
    error: str | None
    created_at: datetime
    delivered_at: datetime | None
