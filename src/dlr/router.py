from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dlr import service
from src.dlr.schemas import DLRPayload

router = APIRouter(prefix="/dlr", tags=["dlr"])


@router.post("/callback")
async def dlr_callback(payload: DLRPayload, db: AsyncSession = Depends(get_db)) -> dict:
    await service.handle_dlr(db, payload.id, payload.status, payload.error)
    return {"success": True}


@router.post("/errback")
async def dlr_errback(payload: DLRPayload, db: AsyncSession = Depends(get_db)) -> dict:
    await service.handle_dlr(db, payload.id, "REJECTED", payload.error or "errback")
    return {"success": True}
