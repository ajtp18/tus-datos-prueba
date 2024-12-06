from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.app.services.users import UserService
from strawberry import type, mutation, field, Schema, Info
from strawberry.scalars import JSON

async def get_context(session: Session):
    return {"service": UserService(session)}

@type
class UserQueries:
    @field
    def hello() -> str:
        return "world"

@type
class UserMutations:
    @mutation
    async def create_user(self, info: Info, email: str, password: str, role: int, metadata: JSON) -> str:
        svc: UserService = info.context["service"]
        await svc.create(email, password, role, metadata)

        user = await svc.get_id_by_email(email)
        assert user is not None

        return str(user)


SCHEMA = Schema(query=UserQueries, mutation=UserMutations)