from tus_datos_prueba.utils.db import __CONN, AsyncSession
from tus_datos_prueba.models import User, Role, RolePerm, Event, Assistant, Session
from typing import Callable
from sqlalchemy import select, func, INTEGER
from prometheus_fastapi_instrumentator.metrics import Info
from prometheus_client import Gauge

# Definir métricas globales
DB_SERVER_TIME_METRIC = Gauge("db_server_time", "Actual time of the server system")
DB_TABLE_COUNT_METRIC = Gauge("db_table_count", "Count total rows per table", labelnames=('count', 'table'))

def db_server_time() -> Callable[[Info], None]:
    async def instrumentation(info: Info):
        async with AsyncSession(__CONN) as session:
            time = await session.scalar(select(func.now()))
            DB_SERVER_TIME_METRIC.set(time.timestamp())
    return instrumentation

def db_table_count() -> Callable[[Info], None]:
    async def instrumentation(info: Info):
        try:
            async with AsyncSession(__CONN) as session:
                models = [User, Role, RolePerm, Event, Assistant, Session]
                for model in models:
                    count_clean = None
                    count = await session.scalar(select(func.count(model.id)))
                    if hasattr(model, 'active'):
                        count_clean = await session.scalar(select(func.sum(func.cast(model.active, INTEGER))))

                    if count_clean is not None:
                        DB_TABLE_COUNT_METRIC.labels(count="dirty", table=model.__tablename__).set(count)
                        DB_TABLE_COUNT_METRIC.labels(count="clean", table=model.__tablename__).set(count_clean)
                    else:
                        DB_TABLE_COUNT_METRIC.labels(count="clean", table=model.__tablename__).set(count)
        except Exception as err:
            print(err)
    return instrumentation
