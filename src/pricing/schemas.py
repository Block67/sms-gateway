import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class UserPriceSet(BaseModel):
    user_id: uuid.UUID
    operator_id: uuid.UUID
    price: Decimal


class UserPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    operator_id: uuid.UUID
    price: Decimal
