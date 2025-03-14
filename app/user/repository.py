from datetime import datetime, timedelta, timezone
from uuid import UUID
import os

from dotenv import load_dotenv
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError


from app.user.models import User
from app.user.schema import AccessToken, BaseUserSchema, UserCreate, UserResponse
from app.system.security.security import get_password_hash, verify_password
from app.config.settings import get_config


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

    async def authenticate(self, email: str, password:str):
        result = await self.db_session.execute(
            select(User).filter_by(email=email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password.")
    
        if not verify_password(password, str(user.password)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password.")

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=token_expires_in)

        payload = {
            'sub': f'{user.uuid}',
            'exp': int(expires_at.timestamp()),
            'user': {
                'uuid': f'{user.uuid}',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            },
        }

        access_token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        return AccessToken(
            token=access_token, 
            token_type='bearer', 
            expires_in=token_expires_in, 
            )
