from fastapi import APIRouter
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.utils.elastic import Elastic
from sqlalchemy import func, select
from tus_datos_prueba.app.models import PingResponse

router = APIRouter()

@router.get("/")
async def ping(session: Session, elastic: Elastic) -> PingResponse:
    health = await elastic.health_report()
    now = await session.scalar(select(func.now()))

    assert health["status"] != 'red'
    
    return PingResponse(ok=True, time=now.isoformat())