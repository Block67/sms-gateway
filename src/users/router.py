from fastapi import APIRouter, Depends

from src.users.dependencies import get_current_user
from src.users.models import User
from src.users.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
