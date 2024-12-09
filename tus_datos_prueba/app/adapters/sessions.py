from strawberry import type, field, mutation, Info
from typing import Optional
from uuid import UUID
from datetime import datetime
from strawberry.scalars import JSON
from tus_datos_prueba.utils.jwt import has_permission

from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.app.services.sessions import SessionService
from tus_datos_prueba.app.services.assistants import AssistantService

from tus_datos_prueba.models.events import EventStatus, AssistantType
from tus_datos_prueba.app.models.sessions import SessionResponse

@type
class SessionQueries:
    @field
    async def session_list(self, info: Info, event_id: UUID, limit: Optional[int] = None, offset: Optional[int] = None) -> list[SessionResponse]:
        has_permission(info.context["session"], "assistants", "list")
        
        svc: SessionService = info.context["session_service"]
        sessions = await svc.list_sessions(event_id, limit, offset)
        return [SessionResponse.from_db(s) for s in sessions]

    @field
    async def session_get_by_id(self, info: Info, id: UUID) -> SessionResponse:
        has_permission(info.context["session"], "assistants", "get")
        
        svc: SessionService = info.context["session_service"]
        session_obj = await svc.get_by_id(id)
        assert session_obj is not None, "Session does not exist or is inactive."
        
        return SessionResponse.from_db(session_obj)

@type
class SessionMutations:
    @mutation
    async def session_create(
        self,
        info: Info,
        event_id: UUID,
        title: str,
        description: str,
        start_date: str,
        end_date: str,
        meta: JSON,
        speaker_id: UUID
    ) -> str:
        has_permission(info.context["session"], "assistants", "create")
        
        event_svc: EventService = info.context["event_service"]
        assistant_svc: AssistantService = info.context["assistant_service"]
        session_svc: SessionService = info.context["session_service"]

        event = await event_svc.get_by_id(event_id)
        assert event is not None and event.active, "Event does not exist or is inactive."
        assert event.status != EventStatus.FINISHED, "Cannot create sessions for a finished event."

        # Title and description validation
        assert title.strip(), "Title cannot be empty."
        assert len(description.split()) <= 500, "Description cannot exceed 500 words."

        # Parse dates
        sd = datetime.fromisoformat(start_date).replace(tzinfo=event.start_date.tzinfo)
        ed = datetime.fromisoformat(end_date).replace(tzinfo=event.end_date.tzinfo)

        print(event.start_date, event.end_date, "x" * 100)

        # Validate session date range within the event
        assert sd >= event.start_date and ed <= event.end_date, "Session must be within the event date range."

        # Speaker validation
        speaker = await assistant_svc.get_by_id(speaker_id)
        assert speaker is not None, "Speaker does not exist."
        assert speaker.type == AssistantType.SPEAKER, "Assigned assistant must be a speaker."

        # Check for overlapping sessions
        conflict = await session_svc.sessions_conflict(event_id, sd, ed)
        assert not conflict, "Sessions cannot overlap."

        # Create session after all validations
        await session_svc.create_session(
            event_id=event_id,
            title=title,
            description=description,
            start_date=sd,
            end_date=ed,
            meta=meta,
            speaker_id=speaker_id
        )

        return "Session created successfully."

    @mutation
    async def session_update(
        self,
        info: Info,
        id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        meta: Optional[JSON] = None,
        speaker_id: Optional[UUID] = None
    ) -> None:
        has_permission(info.context["session"], "assistants", "update")
        
        event_svc: EventService = info.context["event_service"]
        assistant_svc: AssistantService = info.context["assistant_service"]
        session_svc: SessionService = info.context["session_service"]

        session_obj = await session_svc.get_by_id(id)
        assert session_obj is not None, "Session does not exist or is inactive."

        event = session_obj.event
        assert event.active, "Cannot modify sessions of an inactive event."
        assert event.status != EventStatus.FINISHED, "Cannot modify sessions of a finished event."

        # Prepare new values with validations
        new_title = session_obj.title
        new_description = session_obj.description
        new_start_date = session_obj.start_date
        new_end_date = session_obj.end_date
        new_meta = session_obj.meta
        new_speaker_id = session_obj.speaker_id

        if title is not None:
            assert title.strip(), "Title cannot be empty."
            new_title = title

        if description is not None:
            assert len(description.split()) <= 500, "Description cannot exceed 500 words."
            new_description = description

        if start_date is not None:
            sd = datetime.fromisoformat(start_date)
            assert sd >= event.start_date, "Session must start within the event date range."
            new_start_date = sd
        else:
            sd = new_start_date

        if end_date is not None:
            ed = datetime.fromisoformat(end_date)
            assert ed <= event.end_date, "Session must end within the event date range."
            new_end_date = ed
        else:
            ed = new_end_date

        # Check for conflicts if dates changed
        if start_date is not None or end_date is not None:
            conflict = await session_svc.sessions_conflict(event.id, sd, ed, exclude_session_id=id)
            assert not conflict, "Sessions cannot overlap."

        if meta is not None:
            new_meta = meta

        if speaker_id is not None:
            speaker = await assistant_svc.get_by_id(speaker_id)
            assert speaker is not None, "Speaker does not exist."
            assert speaker.type == AssistantType.SPEAKER, "Assigned assistant must be a speaker."
            new_speaker_id = speaker_id

        # After all validations, update the session
        await session_svc.update_session(
            session_obj,
            title=new_title,
            description=new_description,
            start_date=new_start_date,
            end_date=new_end_date,
            meta=new_meta,
            speaker_id=new_speaker_id
        )
    @mutation
    async def session_delete(self, info: Info, id: UUID) -> None:
        has_permission(info.context["session"], "assistants", "delete")
        
        session_svc: SessionService = info.context["session_service"]
        session_obj = await session_svc.get_by_id(id)
        assert session_obj is not None, "Session does not exist or is inactive."

        event = session_obj.event
        assert event.active, "Cannot delete sessions of an inactive event."
        assert event.status != EventStatus.FINISHED, "Cannot delete sessions of a finished event."

        await session_svc.delete_session(session_obj)
        return "Session deleted successfully."