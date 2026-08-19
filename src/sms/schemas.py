from pydantic import BaseModel, Field, HttpUrl


class SMSSendRequest(BaseModel):
    to: str
    text: str = Field(min_length=1, max_length=1600)
    sender: str | None = None
    dlr_url: HttpUrl | None = None
