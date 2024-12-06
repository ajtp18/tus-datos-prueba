from tus_datos_prueba.models._base import ModelBase, UseCreatedAt
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import JSON, UUID as DB_UUID, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from datetime import datetime
from uuid import UUID, uuid4
from enum import IntEnum

from tus_datos_prueba.models.users import User


class EventStatus(IntEnum):
    """
    Event Status
    """

    PENDING = 0
    IN_PROGRESS = 1
    PAUSED = 2
    FINISHED = 3

class Event(UseCreatedAt, ModelBase):
    """
    Events
    """

    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True, default=uuid4)

    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    status: Mapped[EventStatus] = mapped_column(default=EventStatus.PENDING)
    active: Mapped[bool] = mapped_column(default=True)

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    meta: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=True)
    assitant_limit: Mapped[int] = mapped_column()

    created_by_id:  Mapped[UUID] = mapped_column(ForeignKey("users.id")) #TODO: Add cascade
    created_by: Mapped[User] = relationship()

    assistants: Mapped[list["Assistant"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class AssistantType(IntEnum):
    """
    Assistant Type
    """

    STAFF = 0
    SPEAKER = 1
    MAINTAINENCE = 2
    USER = 3
    OWNER = 4


class Assistant(UseCreatedAt, ModelBase):
    """
    Application assistant
    """

    __tablename__ = "assistants"
    
    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    user: Mapped["User"] = relationship()

    email: Mapped[str] = mapped_column(index=True)
    full_name: Mapped[str] = mapped_column()

    active: Mapped[bool] = mapped_column(default=True)
    type: Mapped[AssistantType] = mapped_column(default=AssistantType.USER)

    contact_meta: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=True)

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), index=True)
    event: Mapped["Event"] = relationship(back_populates="assistants")