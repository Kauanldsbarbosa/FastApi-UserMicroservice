import re
from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, constr, field_validator

MIN_NAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6


class BaseUserSchema(BaseModel):
    email: str
    first_name: Annotated[str, constr(min_length=3)]
    last_name: Annotated[str, constr(min_length=3)]
    social_name: Optional[Annotated[str, constr(min_length=3)]] = None
    date_of_birth: date

    class Config:
        from_attributes = True

    @field_validator('first_name')
    def validate_first_name(cls, value):
        if len(value) < MIN_NAME_LENGTH:
            raise ValueError('First name must be at least 3 characters long')
        return value

    @field_validator('last_name')
    def validate_last_name(cls, value):
        if len(value) < MIN_NAME_LENGTH:
            raise ValueError('Last name must be at least 3 characters long')
        return value

    @field_validator('email')
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            raise ValueError('The email is not valid.')

        return email


class UserCreate(BaseUserSchema):
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise ValueError(
                'Password must contain at least one special character'
            )
        return value


class UserResponse(BaseUserSchema):
    uuid: UUID


class AccessToken(BaseModel):
    token: str
    token_type: str = 'bearer'
    expires_in: int
