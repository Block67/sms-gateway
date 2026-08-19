import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.senders.constants import SenderStatus


class SenderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=11, pattern=r"^[A-Za-z0-9]+$")


class SenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    status: SenderStatus
    rejection_reason: str | None
    created_at: datetime
    approved_at: datetime | None


class SenderReject(BaseModel):
    reason: str | None = None
