from tus_datos_prueba.models._base import UseCreatedAt, ModelBase
from tus_datos_prueba.models.roles import Role
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import JSON, UUID as DB_UUID
from sqlalchemy.dialects.postgresql.types import BYTEA
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4

class User(UseCreatedAt, ModelBase):
    """
    Application user
    """

    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(index=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship()

    active: Mapped[bool] = mapped_column(default=True)
    meta: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=True)

    passwords: Mapped[list["UserPassword"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def active_password(self):
        try:
            return next(filter(lambda x: x.active == True, self.passwords))
        except StopIteration:
            raise RuntimeError("the user does not have active password, this error can not be displayed")



class UserPassword(UseCreatedAt, ModelBase):
    """
    User's password references
    """

    __tablename__ = "passwords"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["User"] = relationship(back_populates="passwords")

    active: Mapped[bool] = mapped_column(default=True)
    password: Mapped[bytes] = mapped_column(BYTEA())
