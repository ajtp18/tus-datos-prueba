from strawberry import field, Schema, type
from strawberry.fastapi import GraphQLRouter

from tus_datos_prueba.app.adapters.assistants import AssistantMutations, AssistantQueries
from tus_datos_prueba.app.adapters.events import EventMutations, EventQueries
from tus_datos_prueba.app.adapters.sessions import SessionMutations, SessionQueries
from tus_datos_prueba.app.adapters.users import UserMutations, UserQueries

from tus_datos_prueba.app.services.assistants import AssistantService
from tus_datos_prueba.app.services.events import EventService, SearchEventService
from tus_datos_prueba.app.services.roles import RoleService
from tus_datos_prueba.app.services.sessions import SessionService
from tus_datos_prueba.app.services.users import UserService

from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.utils.elastic import Elastic
from tus_datos_prueba.utils.jwt.auth import UserSession
from tus_datos_prueba.utils.mail import Mail


@type
class Queries(UserQueries, EventQueries, AssistantQueries, SessionQueries):
    @field
    def ping() -> str:
        return "pong"


@type
class Mutations(UserMutations, EventMutations, AssistantMutations, SessionMutations):
    pass


async def get_context(user: UserSession, elastic: Elastic, mail: Mail, session: Session):
    return {
        "session": user,
        "mail": mail,
        "user_service": UserService(session),
        "event_service": EventService(session),
        "search_event_service": SearchEventService(elastic),
        "role_service": RoleService(session),
        "assistant_service": AssistantService(session),
        "session_service": SessionService(session),
    }


schema = Schema(Queries, Mutations)
router = GraphQLRouter(schema, context_getter=get_context)
