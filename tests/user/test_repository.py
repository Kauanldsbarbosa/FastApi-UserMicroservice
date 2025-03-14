from datetime import date
from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from sqlalchemy.future import select
from jose import jwt

from app.user.models import User, ResetPasswordToken
from app.user.repository import UserRepository
from app.user.schema import AccessToken, BaseUserSchema, UserCreate

ALGORITHM = "HS256"
SECRET_KEY='3471f8db81f2c685a7edd5dbea62b6fb77987a548abe9ea42332998deb41b706'


@pytest.mark.asyncio
async def test_create_user(db_session):
    user_data = UserCreate(
        email='validuser@example.com',
        first_name='John',
        last_name='Doe',
        date_of_birth=date(1995, 5, 20),
        password='SecurePass!',
    )
    repository = UserRepository(db_session)

    user = await repository.create_user(user_data)

    result = await db_session.execute(
        select(User).filter_by(email=user_data.email)
    )
    user_on_db = result.scalars().first()

    assert user_on_db is not None
    assert user_on_db.email == user_data.email
    assert user_on_db.first_name == user_data.first_name

    try:
        await db_session.delete(user)
        await db_session.commit()
    except Exception as e:
        print(f'Erro ao deletar usuário: {e}')
        await db_session.rollback()


@pytest.mark.asyncio
async def test_get_user_by_id(db_session, create_user):
    user = create_user
    repository = UserRepository(db_session)

    fetched_user = await repository.get_user_by_id(user.uuid)

    assert fetched_user is not None
    assert fetched_user.email == user.email
    assert fetched_user.first_name == user.first_name
    assert fetched_user.last_name == user.last_name


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session):
    repository = UserRepository(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await repository.get_user_by_id(uuid4())
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_user(db_session, create_user):
    user = create_user
    repository = UserRepository(db_session)
    update_data = BaseUserSchema(
        email='updated@example.com',
        first_name='John',
        last_name='Doe',
        date_of_birth='1995-05-20',
    )

    updated_user = await repository.update_user(user.uuid, update_data)
    assert updated_user.uuid == user.uuid
    assert updated_user.email == update_data.email


@pytest.mark.asyncio
async def test_delete_user(db_session, create_user):
    user = create_user
    repository = UserRepository(db_session)
    await repository.delete_user(user.uuid)
    with pytest.raises(HTTPException) as exc_info:
        await repository.get_user_by_id(user.uuid)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_authenticate(db_session, create_user: User):
    user = create_user
    repository = UserRepository(db_session)
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
        repository = UserRepository(db_session)
        result = await repository.authenticate(
            email='invalid',
            password='invalid!'
        )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_generate_reset_password_token(db_session, create_user: User):
    repository = UserRepository(db_session)
    result = await repository.generate_reset_password_token(create_user.email)

    result = await db_session.execute(
        select(ResetPasswordToken).filter_by(user_id=create_user.uuid)
    )
    token_on_db = result.scalars().first()

    assert token_on_db is not None
    assert token_on_db.user_id == create_user.uuid
    assert token_on_db.token is not None
    assert token_on_db.expires_at is not None

    await db_session.delete(create_user)
    await db_session.commit()
