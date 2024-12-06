from strawberry.fastapi import GraphQLRouter
from tus_datos_prueba.app.adapters.users import get_context, SCHEMA

router = GraphQLRouter(SCHEMA, context_getter=get_context)