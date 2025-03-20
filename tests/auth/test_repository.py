import pytest
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.repository import AuthRepository
from app.auth.schemas import AccessToken
from app.config.settings import get_config
from app.system.security.security import verify_password
from app.user.models import User, ResetPasswordToken

load_dotenv()
token_expires_in = int(get_config().AUTH_TOKEN_EXPIRES)
ALGORITHM = get_config().ALGORITHM
SECRET_KEY = get_config().SECRET_KEY


@pytest.mark.asyncio
async def test_authenticate(db_session, create_user: User):
    user = create_user
    repository = AuthRepository(db_session)
    result = await repository.authenticate(
        email=user.email, password='SecurePass!'
    )
    token: dict = jwt.decode(result.token, SECRET_KEY, algorithms=[ALGORITHM])
    assert result is not None
    assert isinstance(result, AccessToken)
    assert ['sub', 'exp', 'user'] == list(token.keys())
    assert token['user']['uuid'] == str(user.uuid)
    assert token['user']['first_name'] == user.first_name
    assert token['user']['last_name'] == user.last_name
    assert token['user']['email'] == user.email


@pytest.mark.asyncio
async def test_authenticate_with_invalid_credentials(db_session):
    repository = AuthRepository(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await repository.authenticate(email='invalid', password='invalid!')

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_request_password_recovery_token(db_session, create_user: User):
    user = create_user
    repository = AuthRepository(db_session)
    result = await repository.request_password_recovery_token(email=user.email)
    assert result is not None
    assert result is not None
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_change_user_password(db_session:AsyncSession, create_user: User):
    repository = AuthRepository(db_session=db_session)
    token = await repository.request_password_recovery_token(email=create_user.email)
    new_password = 'Test123!'
    await repository.change_user_password(token, new_password=new_password)
    user_result = await db_session.execute(
        select(User).filter(User.uuid == create_user.uuid)
    )
    user = user_result.scalar_one_or_none()

    assert user is not None
    assert verify_password(new_password, create_user.password)

    token_result = await db_session.execute(
        select(ResetPasswordToken).filter(ResetPasswordToken.token == token)
    )
    token_on_db = token_result.scalar_one_or_none()
    assert token_on_db is None

@pytest.mark.asyncio
async def test_change_password_with_invalid_token(db_session:AsyncSession, create_user: User):
    repository = AuthRepository(db_session=db_session)
    with pytest.raises(HTTPException) as exc_info:
        await repository.change_user_password(token='klafsnklSFN', new_password='Test123!')

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        