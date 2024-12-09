from strawberry import type, field, Schema
from strawberry.fastapi import GraphQLRouter
from tus_datos_prueba.app.adapters.assistants import AssistantQueries, AssistantMutations
from tus_datos_prueba.app.adapters.users import UserQueries, UserMutations
from tus_datos_prueba.app.services.assistants import AssistantService
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.app.services.events import EventService, SearchEventService
from tus_datos_prueba.app.services.roles import RoleService
from tus_datos_prueba.utils.jwt.auth import UserSession

from tus_datos_prueba.app.adapters.events import EventQueries, EventMutations
from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.utils.elastic import Elastic


@type
class Queries(UserQueries, EventQueries, AssistantQueries):
    @field
    def ping() -> str:
        return "pong"


@type
class Mutations(UserMutations, EventMutations, AssistantMutations):
    pass


async def get_context(user: UserSession, elastic: Elastic, session: Session):
    return {
        "session": user,
        "user_service": UserService(session),
        "event_service": EventService(session),
        "search_event_service": SearchEventService(elastic),
        "role_service": RoleService(session),
        "assistant_service": AssistantService(session)
    }


schema = Schema(Queries, Mutations)
router = GraphQLRouter(schema, context_getter=get_context)
