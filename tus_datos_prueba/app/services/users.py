from tus_datos_prueba.utils.db import Session
from tus_datos_prueba.models import User, Role, UserPassword
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update, insert
from tus_datos_prueba.utils.password import verify_password, create_password
from uuid import UUID

class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def login(self, email: str, password: str) -> User | None:
        query = select(User).options(joinedload(User.passwords), joinedload(User.role).subqueryload(Role.permissions)).where(User.email == email).limit(1)
        user = await self.session.scalar(query)

        if user is not None and verify_password(password, user.active_password.password):
            return user

    async def create(self, email: str, password: str, role: int, metadata: dict = None):
        user = User()
        user.email = email
        user.role_id = role
        user.meta = metadata
        user.passwords = [UserPassword(password=create_password(password))]

        async with self.session.begin():
            try:
                self.session.add(user)
            except:
                await self.session.rollback()
            else:
                await self.session.commit()

    async def get_id_by_email(self, email: str) -> UUID | None:
        user = await self.session.scalar(select(User.id).where(User.email == email).limit(1))
        
        return user

    async def get_by_id(self, id: UUID) -> User | None:
        user = await self.session.scalar(select(User).where(User.id == id).limit(1))
        
        return user
    
    async def list_users(self, limit: int | None = None, offset: int | None = None) -> list[User]:
        query = select(User)
        
        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        users = list(await self.session.scalars(query))
        return users
    
    async def update(self, user: User):
        await self.session.flush()
        await self.session.commit()

    async def delete(self, user: User):
        await self.session.delete(user)
        await self.session.commit()