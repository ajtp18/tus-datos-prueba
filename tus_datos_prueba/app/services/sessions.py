from sqlalchemy import select, func
from tus_datos_prueba.models.events import Session as Session_model
from tus_datos_prueba.utils.db import Session
from datetime import datetime
from uuid import UUID

class SessionService:
    def __init__(self, session: Session):
        self.session = session

    async def get_by_id(self, session_id: UUID) -> Session_model | None:
        # Filter only active sessions:
        result = await self.session.execute(
            select(Session_model).where(Session_model.id == session_id, Session_model.active == True)
        )
        return result.scalar_one_or_none()

    async def list_sessions(self, event_id: UUID, limit: int | None = None, offset: int | None = None) -> list[Session_model]:
        stmt = select(Session_model).where(Session_model.event_id == event_id, Session_model.active == True)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_session(
        self,
        event_id: UUID,
        title: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        meta: dict,
        speaker_id: UUID
    ) -> Session_model:
        new_session = Session_model(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            meta=meta,
            event_id=event_id,
            speaker_id=speaker_id,
            active=True,
            updated_at=datetime.utcnow()
        )
        self.session.add(new_session)
        await self.session.commit()
        return new_session

    async def update_session(
        self,
        session_obj: Session_model,
        title: str | None = None,
        description: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        meta: dict | None = None,
        speaker_id: UUID | None = None
    ):
        if title is not None:
            session_obj.title = title
        if description is not None:
            session_obj.description = description
        if start_date is not None:
            session_obj.start_date = start_date
        if end_date is not None:
            session_obj.end_date = end_date
        if meta is not None:
            session_obj.meta = meta
        if speaker_id is not None:
            session_obj.speaker_id = speaker_id

        self.session.add(session_obj)
        await self.session.commit()

    async def delete_session(self, session_obj: Session_model):
        # DEsactivate session:
        session_obj.active = False
        self.session.add(session_obj)
        await self.session.commit()

    async def sessions_conflict(self, event_id: UUID, start_date: datetime, end_date: datetime, exclude_session_id: UUID | None = None) -> bool:
        # Filter only active sessions:
        stmt = select(Session_model).where(
            Session_model.event_id == event_id,
            Session_model.active == True,
            (Session_model.start_date <= end_date) & (Session_model.end_date >= start_date)
        )
        if exclude_session_id is not None:
            stmt = stmt.where(Session_model.id != exclude_session_id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None