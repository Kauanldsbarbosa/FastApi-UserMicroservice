from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import jwt
import pytest

from app.user.models import User
from app.config.settings import get_config
from app.auth.repository import AuthRepository
from app.auth.schemas import AccessToken

load_dotenv()
token_expires_in = int(get_config().AUTH_TOKEN_EXPIRES)
ALGORITHM = get_config().ALGORITHM
SECRET_KEY = get_config().SECRET_KEY

@pytest.mark.asyncio
async def test_authenticate(db_session, create_user: User):
    user = create_user
    repository = AuthRepository(db_session)
    result = await repository.authenticate(
        email=user.email,
        password='SecurePass!'
    )
    token:dict = jwt.decode(result.token, SECRET_KEY, algorithms=[ALGORITHM])
    assert result is not None
    assert type(result) == AccessToken
    assert ['sub', 'exp', 'user'] == list(token.keys())
    assert token['user']['uuid'] == str(user.uuid)
    assert token['user']['first_name'] == user.first_name
    assert token['user']['last_name'] == user.last_name
    assert token['user']['email'] == user.email

@pytest.mark.asyncio
async def test_authenticate_with_invalid_credentials(db_session):
    with pytest.raises(HTTPException) as exc_info:
        repository = AuthRepository(db_session)
        await repository.authenticate(
            email='invalid',
            password='invalid!'
        )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Incorrect username or password.'
        