from fastapi import APIRouter, HTTPException
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.models import User
from tus_datos_prueba.app.models.users import LoginClaim
from tus_datos_prueba.utils.jwt import sign_session

router = APIRouter()


@router.post('/login')
async def login(session: Session, claim: LoginClaim) -> str:
    service = UserService(session)
    user = await service.login(claim.email, claim.password)

    if user == None:
        raise HTTPException(401, "bad credentials")

    return sign_session(user)