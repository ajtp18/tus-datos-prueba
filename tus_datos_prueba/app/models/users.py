from strawberry import type
from strawberry.scalars import JSON
from pydantic import BaseModel
from tus_datos_prueba.models import User
from uuid import UUID


class LoginClaim(BaseModel):
    # TODO: enhance validations
    email: str
    password: str


@type
class UserResponse:
    id: UUID
    email: str
    role_id: int
    active: bool
    metadata: JSON | None


    @staticmethod
    def from_db(user: User):
        return UserResponse(
            id=user.id,
            email=user.email,
            role_id=user.role_id,
            active=user.active,
            metadata=user.meta
        )
