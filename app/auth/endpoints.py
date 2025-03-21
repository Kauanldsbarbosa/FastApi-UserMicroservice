from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.schemas import AccessToken, RequestPasswordResetSchema, ResetPasswordSchema
from app.system.database.connection import get_db

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/',
    summary='User authentication',
    description="""
            In this context the email will be used as username
            """,
    response_model=AccessToken,
)
async def auth(
    login_request_form: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db),
):
    repository = AuthRepository(db_session)
    token_data = await repository.authenticate(
        email=login_request_form.username, password=login_request_form.password
    )

    return token_data


@router.post(
    '/password-reset',
    summary='Request password recovery token',
    description="""
            This endpoint is used to request a password recovery token.
            """,
)
async def request_password_recovery_token(
    email: RequestPasswordResetSchema, 
    db_session: AsyncSession = Depends(get_db)
):
    repository = AuthRepository(db_session)
    result = await repository.request_password_recovery_token(email=email.email)
    return {
        'token': result
    }

@router.post(
    '/change-password',
    summary='change user password',
    description="""
            This endpoint is used to change user password.
            """,
)
async def change_password(
    token_and_new_pass: ResetPasswordSchema, 
    db_session: AsyncSession = Depends(get_db)
):
    repository = AuthRepository(db_session)
    await repository.change_user_password(
        new_password=token_and_new_pass.new_password,
        token=token_and_new_pass.token
        )
    return {
        'message ': 'password changed successfully'
    }

