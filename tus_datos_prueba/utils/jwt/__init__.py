from tus_datos_prueba.models import User
from tus_datos_prueba.config import SECRET
from jwt import encode
from datetime import datetime, timedelta


def sign_session(user: User) -> str:
    now = datetime.utcnow()
    expiration = now + timedelta(minutes=30)

    payload = {
        "sub": str(user.id),
        "nbf": now.timestamp(),
        "exp": expiration.timestamp(),
        "perms": user.role.permissions_dict,
    }
    
    return encode(payload, SECRET, algorithm="HS512")