import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    balance: Decimal
    is_test: bool
    is_admin: bool
