from uuid import UUID

from dotenv import load_dotenv
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config.settings import get_config
from app.system.security.security import get_password_hash
from app.user.models import User
from app.user.schema import BaseUserSchema, UserCreate

load_dotenv()
token_expires_in = int(get_config().AUTH_TOKEN_EXPIRES)
ALGORITHM = get_config().ALGORITHM
SECRET_KEY = get_config().SECRET_KEY


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        user.password = get_password_hash(user_data.password)
        self.db_session.add(user)
        await self.db_session.flush()
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: UUID) -> User:
        result = await self.db_session.execute(
            select(User).filter_by(uuid=user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='user not found.'
            )
        return user

    async def update_user(
        self, user_id: UUID, user_data: BaseUserSchema
    ) -> User:
        user = await self.get_user_by_id(user_id)
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)
        await self.db_session.delete(user)
        await self.db_session.commit()
