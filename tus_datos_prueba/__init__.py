from fastapi import FastAPI
from tus_datos_prueba.app.routes.ping import router as ping_router
from tus_datos_prueba.app.routes.users import router as users_router
from tus_datos_prueba.app.routes.graphql import router as graphql_router

app = FastAPI(
    name="TusDatosPrueba",
    version="v0.0.1",
    redoc_url=None,
)

app.include_router(ping_router, prefix="/ping")
app.include_router(users_router, prefix="/users")
app.include_router(graphql_router, prefix="/graphql")