from fastapi import APIRouter
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.utils.elastic import Elastic
from tus_datos_prueba.utils.mail import Mail
from tus_datos_prueba.utils.mail.compose import compose_email
from tus_datos_prueba.config import ADMIN_DOMAIN
from sqlalchemy import func, select
from tus_datos_prueba.app.models import PingResponse

router = APIRouter()

@router.get("/")
async def ping(session: Session, elastic: Elastic, mail: Mail) -> PingResponse:
    health = await elastic.health_report()
    now = await session.scalar(select(func.now()))

    assert health["status"] != 'red'

    mail_content = compose_email(
        "Test mail - Ping",
        "webmaster@" + ADMIN_DOMAIN,
        "Ping got from server\nNote: ping is not supposed to be exposed"
    )
    await mail.send_message(mail_content)
    
    return PingResponse(ok=True, time=now.isoformat())