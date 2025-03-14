from datetime import date
from uuid import UUID

from pydantic import ValidationError
import pytest

from app.user.schema import AccessToken, UserCreate, UserResponse, ResetPasswordSchema, RequestPasswordResetSchema


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

def test_valid_token_response():
    random_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzd' \
    'WIiOiJKb2huIERvZSIsImV4cCI6MTYyNzQ2MjIyMH0.5z1b3'
    token_response = AccessToken(
        token=random_token,
        token_type='bearer',
        expires_in=15,
        )

    assert token_response.token == random_token
    assert token_response.token_type == 'bearer'
    assert token_response.expires_in == 15

def test_invalid_token_response():
    with pytest.raises(ValidationError):
        AccessToken(
            token=None,
            token_type='bearer',
            expires_in=15,
        )

def test_reset_password_schema():
    fake_token = '1a2b3c'
    schema = ResetPasswordSchema(
        new_password='SecurePass!',
        token=fake_token,
    )
    assert schema.new_password == 'SecurePass!'
    assert schema.token == fake_token

def test_invalid_reset_password_schema():
    with pytest.raises(ValidationError):
        ResetPasswordSchema(
            new_password='SecurePass!',
            token=None,
        )

    with pytest.raises(ValidationError):
        ResetPasswordSchema(
            new_password=None,
            token='1a2b3c',
        )

    with pytest.raises(ValidationError):
        ResetPasswordSchema(
            new_password='invalidpass',
            token='1a2b3c',
        )

def test_request_password_reset_schema():
    schema = RequestPasswordResetSchema(
        email='test@email.com'
    )
    assert schema.email == 'test@email.com'

def test_invalid_request_password_reset_schema():
    with pytest.raises(ValidationError):
        RequestPasswordResetSchema(
            email=None
        )
        