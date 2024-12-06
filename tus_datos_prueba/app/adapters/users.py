from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.app.models.users import UserResponse
from tus_datos_prueba.utils.jwt import has_permission
from strawberry import type, mutation, field, Info
from strawberry.scalars import JSON
from uuid import UUID

@type
class UserQueries:
    @field
    async def user_me(self, info: Info) -> UserResponse:
        svc: UserService = info.context["user_service"]

        user = await svc.get_by_id(UUID(info.context["session"]["sub"]))
        assert user is not None

        return UserResponse.from_db(user)
    
    @field
    async def user_list(self, info: Info, limit: int | None = None, offset: int | None = None) -> list[UserResponse]:
        has_permission(info.context["session"], "user", "list")

        svc: UserService = info.context["user_service"]

        users = await svc.list_users(limit, offset)
        
        return [UserResponse.from_db(user) for user in users]


    @field
    async def user_get_by_id(self, info: Info, id: UUID) -> UserResponse:
        has_permission(info.context["session"], "user", "get")

        svc: UserService = info.context["user_service"]

        user = await svc.get_by_id(id)
        assert user is not None

        return UserResponse.from_db(user)


@type
class UserMutations:
    @mutation
    async def user_create(self, info: Info, email: str, password: str, role: int, metadata: JSON) -> str:
        has_permission(info.context["session"], "user", "create")

        svc: UserService = info.context["user_service"]
        await svc.create(email, password, role, metadata)

        user = await svc.get_id_by_email(email)
        assert user is not None

        return str(user)
    
    @mutation
    async def user_update(self, info: Info, id: UUID, email: str | None = None, role: int | None = None, metadata: JSON | None = None) -> None:
        has_permission(info.context["session"], "user", "update")

        svc: UserService = info.context["user_service"]
        user = await svc.get_by_id(id)
        assert user is not None

        if email is not None:
            user.email = email

        if role is not None:
            user.role_id = role

        if metadata is not None:    
            user.meta = metadata

        await svc.update(user)

    @mutation
    async def user_delete(self, info: Info, id: UUID) -> None:
        has_permission(info.context["session"], "user", "delete")

        svc: UserService = info.context["user_service"]
        user = await svc.get_by_id(id)
        assert user is not None

        await svc.delete(user)


