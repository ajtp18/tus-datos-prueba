
from tus_datos_prueba.models.events import Session
from uuid import UUID
from strawberry.scalars import JSON
from strawberry import type

@type
class SessionResponse:
    id: UUID
    title: str
    description: str
    start_date: str
    end_date: str
    meta: JSON
    speaker_id: UUID
    active: bool

    @staticmethod
    def from_db(session: Session):
        return SessionResponse(
            id=session.id,
            title=session.title,
            description=session.description,
            start_date=session.start_date.isoformat(),
            end_date=session.end_date.isoformat(),
            meta=session.meta,
            speaker_id=session.speaker_id,
            active=session.active
        )