import pytest
from dotenv import load_dotenv
from fastapi import status
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.future import select

from app.config.settings import get_config
from app.user.models import ResetPasswordToken, User
from app.auth.repository import AuthRepository
from app.system.security.security import verify_password

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

@pytest.mark.asyncio
async def test_change_password(
    client: AsyncClient, create_user: User, setup_db, db_session
):
    repository = AuthRepository(db_session)
    result = await repository.request_password_recovery_token(email=create_user.email)
    response = await client.post(
        '/auth/change-password',
        json={
            'token': result, 
            'new_password': 'Test123!'
            },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message '] == 'password changed successfully'
    
    user_result = await db_session.execute(
        select(User).filter(User.uuid == create_user.uuid)
    )
    user = user_result.scalar_one_or_none()
    assert user is not None
    token_result = await db_session.execute(
        select(ResetPasswordToken).filter(ResetPasswordToken.token == result)
    )
    token_on_db = token_result.scalar_one_or_none()
    assert token_on_db is None
    await db_session.refresh(create_user)
    assert verify_password('Test123!', create_user.password)
