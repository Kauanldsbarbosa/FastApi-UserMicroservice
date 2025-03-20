import pytest
from dotenv import load_dotenv
from fastapi import status
from httpx import AsyncClient
from jose import jwt

from app.config.settings import get_config
from app.user.models import User

load_dotenv()
token_expires_in = int(get_config().AUTH_TOKEN_EXPIRES)
ALGORITHM = get_config().ALGORITHM
SECRET_KEY = get_config().SECRET_KEY


@pytest.mark.asyncio
async def test_auth(client: AsyncClient, create_user: User, setup_db):
    response = await client.post(
        '/auth/',
        data={'username': create_user.email, 'password': 'SecurePass!'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['token'] is not None
    assert response.json()['token_type'] == 'bearer'

    token = jwt.decode(
        response.json()['token'], SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert token['sub'] == str(create_user.uuid)
    assert token['exp'] is not None
    assert token['user']['first_name'] == create_user.first_name
    assert token['user']['last_name'] == create_user.last_name
    assert token['user']['email'] == create_user.email


@pytest.mark.asyncio
async def test_auth_invalid_password(
    client: AsyncClient, create_user: User, setup_db
):
    response = await client.post(
        '/auth/',
        data={'username': create_user.email, 'password': 'InvalidPass!'},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Incorrect username or password.'


@pytest.mark.asyncio
async def test_request_password_recovery_token(
    client: AsyncClient, create_user: User, setup_db
):
    response = await client.post(
    '/auth/password-reset',
    json={'email': create_user.email},
)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['token'] is not None
    assert isinstance(response.json()['token'], str)
