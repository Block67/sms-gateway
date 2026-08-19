import uuid

from pydantic import BaseModel, ConfigDict, Field


class OperatorCreate(BaseModel):
    prefix: str = Field(min_length=1, max_length=15)
    country_iso: str = Field(min_length=2, max_length=2)
    mcc: str = Field(min_length=1, max_length=3)
    mnc: str = Field(min_length=1, max_length=3)
    name: str = Field(min_length=1, max_length=100)


class OperatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    prefix: str
    country_iso: str
    mcc: str
    mnc: str
    name: str
