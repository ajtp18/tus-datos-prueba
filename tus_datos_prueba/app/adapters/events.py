from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.app.models.events import EventResponse
from tus_datos_prueba.utils.jwt import has_permission
from strawberry import type, mutation, field, Info
from strawberry.scalars import JSON
from uuid import UUID


@type
class EventQueries:
    @field
    async def event_list(self, info: Info, limit: int | None = None, offset: int | None = None) -> list[EventResponse]:
        has_permission(info.context["session"], "events", "list")

        svc: EventService = info.context["event_service"]

        events = await svc.list_events(limit, offset)
        
        return [EventResponse.from_db(event) for event in events]


    @field
    async def event_get_by_id(self, info: Info, id: UUID) -> EventResponse:
        has_permission(info.context["session"], "events", "get")

        svc: EventService = info.context["event_service"]

        event = await svc.get_by_id(id)
        assert event is not None

        return EventResponse.from_db(event)
    

@type
class EventMutations:
    @mutation
    async def event_create(
        self, 
        info: Info, 
        title: str, 
        description: str, 
        start_date: str, 
        end_date: str, 
        meta: JSON, 
        assitant_limit: int
    ) -> str:
        has_permission(info.context["session"], "user", "create")

        svc: EventService = info.context["event_service"]
        await svc.create_event(
            title, 
            description, 
            start_date, 
            end_date,
            meta,
            assitant_limit,
            info.context["session"]["sub"]
        )

        return "Event created successfully"
    
    @mutation
    async def event_update(
        self, 
        info: Info, 
        id: UUID, 
        title: str | None = None, 
        description: str | None = None, 
        start_date: str | None = None, 
        end_date: str | None = None, 
        meta: JSON | None = None, 
        assitant_limit: int | None = None
    ) -> None:
        has_permission(info.context["session"], "user", "update")

        svc: EventService = info.context["event_service"]
        event = await svc.get_by_id(id)
        assert event is not None

        if title is not None:
            event.title = title
        
        if description is not None:
            event.description = description

        if start_date is not None:
            event.start_date = start_date
        
        if end_date is not None:
            event.end_date = end_date
        
        if meta is not None:
            event.meta = meta
        
        if assitant_limit is not None:
            event.assitant_limit = assitant_limit

        await svc.update(event)

    @mutation
    async def event_delete(self, info: Info, id: UUID) -> None:
        has_permission(info.context["session"], "user", "delete")

        svc: EventService = info.context["event_service"]
        event = await svc.get_by_id(id)
        assert event is not None

        await svc.delete(event)