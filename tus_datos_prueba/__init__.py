from fastapi import FastAPI
from tus_datos_prueba.app.routes.ping import router as ping_router
from tus_datos_prueba.app.routes.users import router as users_router
from tus_datos_prueba.app.routes.graphql import router as graphql_router
from tus_datos_prueba.app.middlewares.timing import timing as timing_middleware
from tus_datos_prueba.app.middlewares.log import log as log_middleware
from tus_datos_prueba.app.middlewares.errors import assertion_error, on_error
from prometheus_fastapi_instrumentator import Instrumentator
from tus_datos_prueba.app.metrics.db_status import db_server_time, db_table_count

app = FastAPI(
    name="TusDatosPrueba",
    version="v0.0.1",
    redoc_url=None,
)

instrumentator = (
    Instrumentator()
    .instrument(app)
    .add(db_server_time())
    .add(db_table_count())
)


@app.on_event("startup")
async def _startup():
    instrumentator.expose(app, include_in_schema=False)


app.middleware("http")(timing_middleware)
app.middleware("http")(log_middleware)

app.add_exception_handler(AssertionError, assertion_error)
app.add_exception_handler(ValueError, assertion_error)
app.add_exception_handler(Exception, on_error)

app.include_router(ping_router, prefix="/ping")
app.include_router(users_router, prefix="/users")
app.include_router(graphql_router, prefix="/graphql")