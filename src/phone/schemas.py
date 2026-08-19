from pydantic import BaseModel


class PhoneInfo(BaseModel):
    e164: str
    country_code: str | None
    calling_code: int
