from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User
from app.user.schema import BaseUserSchema, UserCreate


@pytest.mark.asyncio
async def test_create_user(client, setup_db):
    user_data = UserCreate(
        email='testuser@example.com',
        first_name='Jane',
        last_name='Doe',
        date_of_birth='1990-05-20',
        password='SecurePass!',
    )

    data_dict = user_data.model_dump()

    data_dict['date_of_birth'] = user_data.date_of_birth.isoformat()

    response = await client.post('/user/', json=data_dict)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['email'] == user_data.email
    assert response.json()['first_name'] == user_data.first_name
    assert response.json()['last_name'] == user_data.last_name


@pytest.mark.asyncio
async def test_get_user(client, create_user: User, setup_db):
    user_id = create_user.uuid

    response = await client.get(f'/user/{user_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == create_user.email
    assert response.json()['first_name'] == create_user.first_name
    assert response.json()['last_name'] == create_user.last_name


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient, setup_db):
    non_existent_user_id = uuid4()

    response = await client.get(f'/user/{non_existent_user_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert str(response.json()['detail']).lower() == 'user not found.'


@pytest.mark.asyncio
async def test_update_user(client, create_user: User, setup_db):
    updated_data = BaseUserSchema(
        email='updateduser@example.com',
        first_name='UpdatedFirst',
        last_name='UpdatedLast',
        date_of_birth='1995-05-20',
    )

    data_dict = updated_data.model_dump()

    data_dict['date_of_birth'] = updated_data.date_of_birth.isoformat()
    response = await client.put(f'/user/{create_user.uuid}', json=data_dict)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == updated_data.email
    assert response.json()['first_name'] == updated_data.first_name
    assert response.json()['last_name'] == updated_data.last_name


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, create_user: User, setup_db):
    response = await client.delete(f'/user/{create_user.uuid}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == 'User deleted successfully.'


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient, setup_db):
    non_existent_user_id = uuid4()

    response = await client.delete(f'/user/{non_existent_user_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'user not found.'
