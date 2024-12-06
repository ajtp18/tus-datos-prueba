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
        assitant_limit: int,
        created_by_id: UUID,
    ) -> UUID:
        event = Event()
        event.title
        event.description
        event.start_date
        event.end_date
        event.meta
        event.assitant_limit
        event.created_by_id 

        async with self.session.begin():
            try:
                self.session.add(event)
            except:
                await self.session.rollback()
            else:
                await self.session.commit()

        await self.session.refresh(event)

        return event.id
