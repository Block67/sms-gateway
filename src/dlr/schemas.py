from pydantic import BaseModel


class DLRPayload(BaseModel):
    id: str
    status: str
    error: str | None = None
