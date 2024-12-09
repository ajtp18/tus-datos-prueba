from datetime import datetime
from tus_datos_prueba.app.services.events import EventService, SearchEventService
from tus_datos_prueba.app.models.events import EventResponse
from tus_datos_prueba.models.events import EventStatus
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

    @field
    async def event_search(
        self,
        info: Info,
        search: str,
        assitant_limit: int | None = None,
        start_date: tuple[str, str] | None = None,
        assistant_count: tuple[int, int] | None = None,
        location: str | None = None,
        category: str | None = None
    ) -> list[EventResponse]:
        has_permission(info.context["session"], "events", "list")

        svc: EventService = info.context["event_service"]
        svc_search: SearchEventService = info.context["search_event_service"]

        props = dict()

        if assitant_limit is not None:
            props['assitant_limit'] = assitant_limit

        if start_date is not None:
            props['start_date'] = start_date

        if assistant_count is not None:
            props['assistant_count'] = assistant_count

        if location is not None:
            props['location'] = location

        if category is not None:
            props['category'] = category


        result = await svc_search.search(search, props)
        
        events = [await svc.get_by_id(id) for id in result]
        events = [EventResponse.from_db(event) for event in events]

        return events
    

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
        has_permission(info.context["session"], "events", "create")

        # Title not empty
        assert title.strip(), "Title is required"

        # Description not to long
        assert len(description.split()) <= 500, "Description is too long"

        # parser date
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        assert end >= start, "End date must be greater than start date"

        assert assitant_limit > 10, "Assistant limit must be greater than 10"

        svc: EventService = info.context["event_service"]

        # events cannot overlap their dates
        assert await svc.events_conflict(start, end), "Events cannot overlap their dates"

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
        assitant_limit: int | None = None,
        status: int | None = None
    ) -> None:
        has_permission(info.context["session"], "events", "update")

        svc: EventService = info.context["event_service"]
        event = await svc.get_by_id(id)
        assert event is not None

        old_status = event.status

        # if the status in event is FINISHED, the event cannot be updated
        if old_status == 3:
            if any([title, description, start_date, end_date, meta, assitant_limit]):
                raise Exception("Event is finished, cannot be updated")

        if title is not None:
            assert title.strip(), "Title is required"
            event.title = title
        
        if description is not None:
            assert len(description.split()) <= 500, "Description is too long"
            event.description = description

        if start_date is not None:
            start = datetime.fromisoformat(start_date)

            actual_end = datetime.fromisoformat(end_date if end_date is not None else event.end_date)
            assert actual_end >= start, "the start date cannot be greater than the end date."

            assert not await svc.events_conflict(start_date, (end_date if end_date else event.end_date), exclude_event_id=id), "Las fechas del evento se cruzan con otro evento."
            event.start_date = start_date
        
        if end_date is not None:
            end = datetime.fromisoformat(end_date)
    
            actual_start = datetime.fromisoformat(start_date if start_date else event.start_date)
            assert end >= actual_start, "the end date cannot be less than the start date."

            assert not await svc.events_conflict((start_date if start_date else event.start_date), end_date, exclude_event_id=id), "Las fechas del evento se cruzan con otro evento."
            event.end_date = end_date

        if meta is not None:
            event.meta = meta
        
        if assitant_limit is not None:
            assert assitant_limit > 10, "Assistant limit must be greater than 10"
            event.assitant_limit = assitant_limit

        if status is not None:
            # PENDING -> PAUSED/IN PROGRESS
            if old_status == EventStatus.PENDING:
                assert status in [EventStatus.PAUSED, EventStatus.IN_PROGRESS], "Status must be IN PROGRESS or PAUSED"
            # IN PROGRESS -> PAUSED/FINISHED
            elif old_status == EventStatus.IN_PROGRESS:
                assert status in [EventStatus.PAUSED, EventStatus.FINISHED], "Status must be PAUSED or FINISHED"
            # PAUSED -> IN PROGRESS/FINISHED
            elif old_status == EventStatus.PAUSED:
                assert status in [EventStatus.IN_PROGRESS, EventStatus.FINISHED], "Status must be IN PROGRESS or FINISHED"
            
            event.status = status

        await svc.update(event)

    @mutation
    async def event_delete(self, info: Info, id: UUID) -> None:
        has_permission(info.context["session"], "events", "delete")

        svc: EventService = info.context["event_service"]
        event = await svc.get_by_id(id)
        assert event is not None

        await svc.delete(event)
