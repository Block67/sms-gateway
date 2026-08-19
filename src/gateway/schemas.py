from pydantic import BaseModel


class GatewaySendResult(BaseModel):
    success: bool
    provider_message_id: str | None
    description: str
