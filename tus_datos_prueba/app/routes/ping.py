from fastapi import APIRouter
from tus_datos_prueba.utils.db import Session
from sqlalchemy import func, select
from tus_datos_prueba.app.models import PingResponse

router = APIRouter()

@router.get("/")
async def ping(session: Session) -> PingResponse:
    now = await session.scalar(select(func.now()))
    
    return PingResponse(ok=True, time=now.isoformat())