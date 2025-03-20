from pydantic import ValidationError
import pytest
from app.auth.schemas import AccessToken, RequestPasswordResetSchema, ResetPasswordSchema


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
        