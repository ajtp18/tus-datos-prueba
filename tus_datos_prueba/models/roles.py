from tus_datos_prueba.models._base import ModelBase, UseCreatedAt
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import JSON, UUID as DB_UUID
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4



class RolePerm(ModelBase):
    """
    Resource access permission
    """

    __tablename__ = "role__perms"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True, default=uuid4)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    role: Mapped["Role"] = relationship(back_populates="permissions")

    resource: Mapped[str] = mapped_column()
    verbs: Mapped[list[str]] = mapped_column(JSON(none_as_null=True))



class Role(UseCreatedAt, ModelBase):
    """
    RBAC Access Handler
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column()
    role_slug: Mapped[str] = mapped_column(unique=True)

    permissions: Mapped[list["RolePerm"]] = relationship(back_populates="role", cascade="all, delete-orphan")

    @property
    def permissions_dict(self):
        return {perm.resource: perm.verbs for perm in self.permissions}
