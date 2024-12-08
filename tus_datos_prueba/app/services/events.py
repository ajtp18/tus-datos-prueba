from sqlalchemy import select
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.models import Event
from datetime import datetime
from uuid import UUID

class EventService:
    def __init__(self, session: Session):
        self.session = session
    
    async def create_event(
        self, 
        title: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        meta: dict,
        assistant_limit: int,
        created_by_id: UUID,
    ) -> UUID:
        event = Event()
        event.title = title
        event.description = description
        event.start_date = start_date
        event.end_date = end_date
        event.meta = meta
        event.assitant_limit = assistant_limit
        event.created_by_id = created_by_id
        event.updated_at = datetime.utcnow()

        async with self.session.begin():
            try:
                self.session.add(event)
            except:
                await self.session.rollback()
                raise
            else:
                await self.session.commit()

        await self.session.refresh(event)

        return event.id
    
    async def get_by_id(self, id: UUID) -> Event | None:
        event = await self.session.scalar(select(Event).where(Event.id == id).limit(1))
        
        return event
    
    async def list_events(self, limit: int | None = None, offset: int | None = None) -> list[Event]:
        query = select(Event)
        
        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        events = list(await self.session.scalars(query))
        return events
    
    async def update(self, event: Event):
        await self.session.flush()
        await self.session.commit()

    async def delete(self, event: Event):
        await self.session.delete(event)
        await self.session.commit()
