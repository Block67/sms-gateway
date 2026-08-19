from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.operators import service
from src.operators.models import Operator
from src.operators.schemas import OperatorCreate, OperatorRead
from src.users.dependencies import get_current_admin
from src.users.models import User

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("", response_model=OperatorRead, status_code=status.HTTP_201_CREATED)
async def create_operator(
    payload: OperatorCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> Operator:
    return await service.create_operator(db, payload)


@router.get("", response_model=list[OperatorRead])
async def list_operators(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[Operator]:
    return await service.list_operators(db)
