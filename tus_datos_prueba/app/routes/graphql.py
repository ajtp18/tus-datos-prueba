from strawberry import type, field, Schema
from strawberry.fastapi import GraphQLRouter
from tus_datos_prueba.app.adapters.users import UserQueries, UserMutations
from tus_datos_prueba.app.services.users import UserService
from tus_datos_prueba.app.services.events import EventService
from tus_datos_prueba.utils.jwt.auth import UserSession
from tus_datos_prueba.utils.db import Session


@type
class Queries(UserQueries):
    @field
    def ping() -> str:
        return "pong"


@type
class Mutations(UserMutations):
    pass


async def get_context(user: UserSession, session: Session):
    return {
        "session": user,
        "user_service": UserService(session),
        "event_service": EventService(session),
    }


schema = Schema(Queries, Mutations)
router = GraphQLRouter(schema, context_getter=get_context)
