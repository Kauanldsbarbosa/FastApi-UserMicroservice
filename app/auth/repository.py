from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.user.models import User
from app.system.security.security import verify_password
from app.auth.schemas import AccessToken
from app.config.settings import get_config


load_dotenv()
token_expires_in = int(get_config().AUTH_TOKEN_EXPIRES)
ALGORITHM = get_config().ALGORITHM
SECRET_KEY = get_config().SECRET_KEY



class AuthRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

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
    