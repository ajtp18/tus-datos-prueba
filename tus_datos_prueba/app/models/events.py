from strawberry import type
from strawberry.scalars import JSON
from tus_datos_prueba.models import Event
from uuid import UUID

@type
class EventResponse:
    id: UUID
    title: str
    description: str
    start_date: str
    end_date: str
    status: int
    owner: UUID

    @staticmethod
    def from_db(event: Event):
        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_date=event.start_date,
            end_date=event.end_date,
            status=event.status,
            owner=event.created_by_id
        )