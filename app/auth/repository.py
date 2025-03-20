from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.schemas import AccessToken
from app.config.settings import get_config
from app.system.security.security import verify_password, get_password_hash
from app.user.models import ResetPasswordToken, User
from app.user.repository import UserRepository

load_dotenv()
token_expires_in = int(get_config().AUTH_TOKEN_EXPIRES)
ALGORITHM = get_config().ALGORITHM
SECRET_KEY = get_config().SECRET_KEY


class AuthRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # TODO: improve this function
    async def authenticate(self, email: str, password: str):
        result = await self.db_session.execute(
            select(User).filter_by(email=email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password.',
            )

        if not verify_password(password, str(user.password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password.',
            )

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=token_expires_in
        )

        payload = {
            'sub': f'{user.uuid}',
            'exp': int(expires_at.timestamp()),
            'user': {
                'uuid': f'{user.uuid}',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            },
        }

        access_token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        return AccessToken(
            token=access_token,
            token_type='bearer',
            expires_in=token_expires_in,
        )

    async def request_password_recovery_token(
        self, email: str
    ):
        user_result = await self.db_session.execute(
            select(User).filter(User.email == email)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return None

        token = await self.create_token(user)
        # TODO: send email with token
        return token
    
    async def change_user_password(self, token: str, new_password:str):
        token_on_db = await self.find_token(token)
        if not token_on_db:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This token is not valid."
                )
        if token_on_db.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="The token is expired"
            )
        
        update_user:User = await UserRepository(self.db_session).get_user_by_id(
            user_id=token_on_db.user_id
            )
        update_user.password = get_password_hash(new_password)
        
        self.db_session.add(update_user)
        await self.db_session.delete(token_on_db)
        await self.db_session.commit()
        
    async def create_token(self, user: User) -> str:
        token = ResetPasswordToken(user_id=user.uuid)
        self.db_session.add(token)
        await self.db_session.flush()
        await self.db_session.commit()
        await self.db_session.refresh(token)
        return token.token

    async def find_token(self, token:str):
        result = await self.db_session.execute(
            select(ResetPasswordToken).filter(
                ResetPasswordToken.token == token
            )
        )
        token_on_db = result.scalar_one_or_none()
        return token_on_db
