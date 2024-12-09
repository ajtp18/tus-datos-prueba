import re
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.app.services.roles import RoleService
from tus_datos_prueba.app.models.users import UserResponse
from tus_datos_prueba.utils.jwt import has_permission
from tus_datos_prueba.config import ADMIN_DOMAIN
from strawberry import type, mutation, field, Info
from strawberry.scalars import JSON
from uuid import UUID

PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])(?!.*20\d{2}).{8,}$')

def validate_password(password: str) -> bool:
    if not PASSWORD_REGEX.match(password):
        raise ValueError("Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number and 1 special character")

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
    async def user_create(self, info: Info, email: str, password: str, role: str, metadata: JSON) -> str:
        has_permission(info.context["session"], "user", "create")

        svc: UserService = info.context["user_service"]
        svc_role: RoleService = info.context["role_service"]

        claim_role_id = await svc_role.get_id_by_slug(role)

        # validate admin with domain
        admin_role_id = await svc_role.get_id_by_slug('administrator')
        if claim_role_id == admin_role_id and not email.endswith(ADMIN_DOMAIN):
            raise Exception("Admin users must have a domain email")
        
        # validate metadata required fields
        assert 'full_name' in metadata and 'job' in metadata, "metadata must have 'fullname' and 'job'."
        
        #validate password
        validate_password(password)

        #create user
        await svc.create(email, password, claim_role_id, metadata)

        user = await svc.get_id_by_email(email)
        assert user is not None

        return str(user)
    
    @mutation
    async def user_update(self, info: Info, id: UUID, email: str | None = None, role: str | None = None, metadata: JSON | None = None) -> None:
        has_permission(info.context["session"], "user", "update")

        svc: UserService = info.context["user_service"]
        svc_role: RoleService = info.context["role_service"]

        claim_role_id = await svc_role.get_id_by_slug(role)

        user = await svc.get_by_id(id)
        assert user is not None

        new_role = claim_role_id if claim_role_id is not None else user.role_id
        new_email = email if email is not None else user.email

        # validate admin with domain
        admin_role_id = await svc_role.get_id_by_slug('administrator')
        if new_role == admin_role_id and not new_email.endswith(ADMIN_DOMAIN):
            raise Exception("Admin users must have a domain email")

        if email is not None:
            user.email = email

        if role is not None:
            user.role_id = new_role

        if metadata is not None:    
            if not isinstance(metadata, dict):
                raise Exception("Metadata must be a dictionary")
            if "full_name" not in metadata and "job" not in metadata:
                raise Exception("Metadata must have 'full_name' and 'job' keys")
            user.meta = metadata

        await svc.update(user)

    @mutation
    async def user_delete(self, info: Info, id: UUID) -> None:
        has_permission(info.context["session"], "user", "delete")

        svc: UserService = info.context["user_service"]
        user = await svc.get_by_id(id)
        assert user is not None

        await svc.delete(user)


