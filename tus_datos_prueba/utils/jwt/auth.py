from typing import Annotated
from fastapi import Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.utils.jwt import validate_session, UserPayload
from tus_datos_prueba.models import User
from sqlalchemy import select, func
from uuid import UUID
from jwt.exceptions import PyJWTError

class JWTBearerAuth(HTTPBearer):
    def __init__(self):
        super().__init__(auto_error=True)

    async def __call__(self, request: Request, session: Session) -> UserPayload:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        try:
            payload = validate_session(creds.credentials)
        except PyJWTError as err:
            raise HTTPException(401, f"Error initializing session: {str(err)}")
        else:
            count = await session.scalar(select(func.count(User.id)).where(User.id == UUID(payload["sub"]), User.active == True))
            assert count == 1

            return payload


UserSession = Annotated[UserPayload, Depends(JWTBearerAuth())]
