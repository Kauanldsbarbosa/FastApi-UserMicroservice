from datetime import date
from uuid import UUID

import pytest

from app.user.schema import UserCreate, UserResponse


def test_invalid_email():
    with pytest.raises(ValueError, match='The email is not valid.'):
        UserCreate(
            email='invalid-email',
            first_name='Valid',
            last_name='User',
            date_of_birth=date(2000, 1, 1),
            password='Valid123!',
        )


def test_invalid_first_name():
    with pytest.raises(
        ValueError, match='First name must be at least 3 characters long'
    ):
        UserCreate(
            email='valid@example.com',
            first_name='Jo',
            last_name='User',
            date_of_birth=date(2000, 1, 1),
            password='Valid123!',
        )


def test_invalid_last_name():
    with pytest.raises(
        ValueError, match='Last name must be at least 3 characters long'
    ):
        UserCreate(
            email='valid@example.com',
            first_name='Valid',
            last_name='Us',
            date_of_birth=date(2000, 1, 1),
            password='Valid123!',
        )


def test_invalid_password():
    with pytest.raises(
        ValueError, match='Password must be at least 6 characters long'
    ):
        UserCreate(
            email='valid@example.com',
            first_name='Valid',
            last_name='User',
            date_of_birth=date(2000, 1, 1),
            password='123!',
        )

    with pytest.raises(
        ValueError,
        match='Password must contain at least one special character',
    ):
        UserCreate(
            email='valid@example.com',
            first_name='Valid',
            last_name='User',
            date_of_birth=date(2000, 1, 1),
            password='Valid123',
        )


def test_valid_user():
    user = UserCreate(
        email='validuser@example.com',
        first_name='John',
        last_name='Doe',
        date_of_birth=date(1995, 5, 20),
        password='SecurePass!',
    )
    assert user.email == 'validuser@example.com'
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.date_of_birth == date(1995, 5, 20)
    assert user.password == 'SecurePass!'


def test_valid_user_response():
    user_response = UserResponse(
        uuid=UUID('123e4567-e89b-12d3-a456-426614174000'),
        email='validuser@example.com',
        social_name=None,
        first_name='John',
        last_name='Doe',
        date_of_birth=date(1995, 5, 20),
    )
    assert user_response.uuid == UUID('123e4567-e89b-12d3-a456-426614174000')
    assert user_response.email == 'validuser@example.com'
    assert user_response.social_name is None
    assert user_response.first_name == 'John'
    assert user_response.last_name == 'Doe'
    assert user_response.date_of_birth == date(1995, 5, 20)
