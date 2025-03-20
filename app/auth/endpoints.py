from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.schemas import AccessToken
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
