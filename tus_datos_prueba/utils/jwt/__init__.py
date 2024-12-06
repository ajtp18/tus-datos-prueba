from fastapi import HTTPException
from tus_datos_prueba.models import User
from tus_datos_prueba.config import SECRET
from jwt import encode, decode
from datetime import datetime, timedelta, timezone
from typing import TypedDict


class UserPayload(TypedDict):
    sub: str
    nbf: float
    exp: float
    perms: dict[str, list[str]]


def sign_session(user: User) -> str:
    now = datetime.now(tz=timezone.utc)
    expiration = now + timedelta(minutes=30)

    payload: UserPayload = {
        "sub": str(user.id),
        "nbf": now.timestamp(),
        "exp": expiration.timestamp(),
        "perms": user.role.permissions_dict,
    }
    
    return encode(payload, SECRET, algorithm="HS512")

def validate_session(jwt: str) -> UserPayload:
    return decode(jwt, SECRET, algorithms=["HS512"])


def has_permission(token: UserPayload, resource: str, verb: str) -> bool:
    ok = resource in token["perms"] and verb in token["perms"][resource]
    if not ok:
        raise HTTPException(403, f"you does not have permission to {resource}.{verb}")
