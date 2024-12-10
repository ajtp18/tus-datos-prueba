from tus_datos_prueba.utils.db import __CONN, AsyncSession
from tus_datos_prueba.models import User, Role, RolePerm, Event, Assistant, Session
from typing import Callable
from sqlalchemy import select, func, INTEGER
from prometheus_fastapi_instrumentator.metrics import Info
from prometheus_client import Gauge

def db_server_time() -> Callable[[Info], None]:
    METRIC = Gauge("db_server_time", "Actual time of the server system")

    async def instrumentation(info: Info):
        async with AsyncSession(__CONN) as session:
            time = await session.scalar(select(func.now()))
            METRIC.set(time.timestamp())

    return instrumentation

def db_table_count() -> Callable[[Info], None]:
    METRIC = Gauge("db_table_count", "Count total rows per table", labelnames=('count', 'table'))

    async def instrumentation(info: Info):
        try:
            async with AsyncSession(__CONN) as session:
                models = [User, Role, RolePerm, Event, Assistant, Session]
                for model in models:
                    count_clean = None
                    count = await session.scalar(select(func.count(model.id)))
                    print(count)
                    if hasattr(model, 'active'):
                        count_clean = await session.scalar(select(func.sum(func.cast(model.active, INTEGER))))

                    if count_clean is not None:
                        METRIC.labels(count="dirty", table=model.__tablename__).set(count)
                        METRIC.labels(count="clean", table=model.__tablename__).set(count_clean)
                    else:
                        METRIC.labels(count="clean", table=model.__tablename__).set(count)
        except Exception as err:
            print(err)

    return instrumentation