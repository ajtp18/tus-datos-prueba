from sqlalchemy import select, func
from tus_datos_prueba.models.events import Assistant
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.utils.elastic import Elastic
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
        query = select(Event).where(Event.id == id, Event.active == True).limit(1)

        return await self.session.scalar(query)
    
    async def list_events(self, limit: int | None = None, offset: int | None = None) -> list[Event]:
        query = select(Event).where(Event.active == True)
        
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
        event.active = False
        await self.session.flush()
        await self.session.commit()

    async def validate_if_event_is_full(self, event_id: UUID) -> bool:
        event = await self.get_by_id(event_id)
        query = select(func.count(Assistant.id)).where(Assistant.event_id == event_id)

        current_count_assistant = await self.session.scalar(query)

        return current_count_assistant > event.assitant_limit
    
    async def events_conflict(self, start_date: datetime, end_date: datetime) -> bool:
        query = select(func.count(Event)).where(
            (Event.start_date <= start_date) & (Event.end_date >= start_date) |
            (Event.start_date <= end_date) & (Event.end_date >= end_date)
        )

        events_conflicted = await self.session.scalars(query)

        return events_conflicted > 0


SearchProps = dict[str, str | tuple[str, str]]


class SearchEventService:
    def __init__(self, elastic: Elastic):
        self.elastic_search = elastic

    # search("evento nuevo", {"start_date": ["2024-10-10", "2024-10-11"], "assistant_count": [1, 10], "assitant_limit": 1, "location": "cartagena", "category": "tecg"})
    async def search(self, text_search: str, props: SearchProps | None = None) -> list[UUID]:
        sort = [
            {
                "_score": {"order": "desc"}
            },
            {
                "start_date": {"order": "desc"}
            }
        ]

        main_query = {
            "query_string": {
                "query": text_search,
                "fields": ["title", "description"]
            }
        }

        sidecar = list()

        if "assitant_limit" in props:
            sidecar.append({
                "term": {
                    "assitant_limit": props["assitant_limit"]
                }
            })

        if "start_date" in props and isinstance(props["start_date"], list) and len(props["start_date"]) == 2:
            sidecar.append({
                "range": {
                    "start_date": {
                        "gte": props["start_date"][0],
                        "lte": props["start_date"][1]
                    }
                }
            })


        if "assistant_count" in props and isinstance(props["assistant_count"], list) and len(props["assistant_count"]) == 2:
            sidecar.append({
                "range": {
                    "assistant_count": {
                        "gte": props["assistant_count"][0],
                        "lte": props["assistant_count"][1]
                    }
                }
            })

        if "location" in props:
            sidecar.append({
                "query_string": {
                    "query": props["location"],
                    "fields": ["metadata.location"]
                }
            })

        if "category" in props:
            sidecar.append({
                "query_string": {
                    "query": props["category"],
                    "fields": ["metadata.category"]
                }
            })

        query = {
            "bool": {
                "must": main_query,
                "should": sidecar
            }
        }

        result = await self.elastic_search.search(source=False, fields=["id"], query=query, sort=sort)
        return list(map(lambda hit: UUID(hit['fields']['id'][0]), result['hits']['hits']))