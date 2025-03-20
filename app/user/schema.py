from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, constr, field_validator

from app.user.utils.validators import validate_email, validate_password

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
    def validate_email(cls, value):
        return validate_email(value)


class UserCreate(BaseUserSchema):
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        return validate_password(value)


class UserResponse(BaseUserSchema):
    uuid: UUID
