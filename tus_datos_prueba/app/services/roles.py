from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.models import  Role
from sqlalchemy import select

class RoleService:
    def __init__(self, session: Session):
        self.session = session

    async def get_id_by_slug(self, slug: str) -> int | None:
        query = select(Role.id).where(Role.role_slug == slug).limit(1)

        return await self.session.scalar(query)