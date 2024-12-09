from sqlalchemy import select
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.models import Assistant
from uuid import UUID

class AssistantService:
    def __init__(self, session: Session):
        self.session = session

    async def create_assistant(
        self,
        event_id: UUID,
        user_id: UUID,
        email: str,
        full_name: str,
        type: int,
        meta: dict,
        contact_meta: dict,
    ) -> UUID:
        assistant = Assistant()
        assistant.event_id = event_id
        assistant.user_id = user_id
        assistant.email = email
        assistant.full_name = full_name
        assistant.type = type
        assistant.meta = meta
        assistant.contact_meta = contact_meta

        try:
            self.session.add(assistant)
        except:
            await self.session.rollback()
            raise
        else:
            await self.session.commit()

        await self.session.refresh(assistant)

        return assistant.id
    
    async def get_by_id(self, id: UUID) -> Assistant | None:

        assistant = await self.session.scalar(select(Assistant).where(Assistant.id == id).limit(1))
        
        return assistant
    
    async def list_assistants(self, limit: int | None = None, offset: int | None = None) -> list[Assistant]:
        query = select(Assistant)
        
        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        assistants = list(await self.session.scalars(query))
        return assistants
    
    async def update(self, id: UUID, email: str | None = None, full_name: str | None = None, type: int | None = None, meta: dict | None = None, contact_meta: dict | None = None) -> None:
        assistant = await self.get_by_id(id)
        if assistant is None:
            return

        if email is not None:
            assistant.email = email
        if full_name is not None:
            assistant.full_name = full_name
        if type is not None:
            assistant.type = type
        if meta is not None:
            assistant.meta = meta
        if contact_meta is not None:
            assistant.contact_meta = contact_meta

        try:
            self.session.add(assistant)
        except:
            await self.session.rollback()
            raise
        else:
            await self.session.commit()

    async def delete(self, assistant: Assistant) -> None:
        await self.session.delete(assistant)
        await self.session.commit()