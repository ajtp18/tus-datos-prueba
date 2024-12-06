from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from tus_datos_prueba.config import POSTGRES_URI, IS_DEBUG

__CONN = create_async_engine(POSTGRES_URI, echo=IS_DEBUG)


async def get_session() -> AsyncSession:
    global __CONN
    async with AsyncSession(__CONN) as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session, use_cache=False)]