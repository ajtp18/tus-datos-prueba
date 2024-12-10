from fastapi import Depends
from typing import Annotated
from aiosmtplib import SMTP
from tus_datos_prueba.config import MAIL_HOST, MAIL_USER, MAIL_PASSWORD, MAIL_FROM, MAIL_TLS


async def get_client() -> SMTP:
    host, port = MAIL_HOST.split(':')
    mail = SMTP(hostname=host, port=port, username=MAIL_USER, password=MAIL_PASSWORD, start_tls=MAIL_TLS)
    await mail.connect()
    yield mail
    mail.close()


Mail = Annotated[SMTP, Depends(get_client)]