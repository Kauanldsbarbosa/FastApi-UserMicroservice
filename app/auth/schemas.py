from pydantic import BaseModel, field_validator

from app.user.utils.validators import validate_email, validate_password


class AccessToken(BaseModel):
    token: str
    token_type: str = 'bearer'
    expires_in: int


class ResetPasswordSchema(BaseModel):
    new_password: str
    token: str

    @field_validator('new_password')
    def validate_new_password(cls, value):
        return validate_password(value)


class RequestPasswordResetSchema(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, value):
        return validate_email(value)
    