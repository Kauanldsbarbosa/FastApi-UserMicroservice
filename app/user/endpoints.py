from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.system.database.connection import get_db
from app.user.repository import UserRepository
from app.user.schema import AccessToken, BaseUserSchema, UserCreate, UserResponse
from app.user.utils import get_current_user

router = APIRouter(prefix='/user', tags=['Users'])


@router.post(
    '/',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new user.',
    description="""
    First name and last name must be longer than 3 characters
    and password must be at least 6 characters long and contain
    a special character.
    """,
)
async def create_user(
    user_data: UserCreate, db_session: AsyncSession = Depends(get_db)
):
    repository = UserRepository(db_session=db_session)
    user = await repository.create_user(user_data=user_data)
    return user


@router.get(
    '/{user_id}',
    response_model=UserResponse,
    summary='Retrieve a user by their ID.',
)
async def get_user(
    user_id: UUID, 
    db_session: AsyncSession = Depends(get_db), 
    user_uuid_token: dict = Depends(get_current_user)
    ):	
    repository = UserRepository(db_session=db_session)
    user = await repository.get_user_by_id(user_id=user_id)
    return UserResponse.model_validate(user)


@router.put(
    '/{user_id}',
    response_model=UserResponse,
    summary="Update an existing user's details.",
    description="""
            First name and last name must be longer than 3 characters
            """,
)
async def update_user(
    user_id: UUID,
    user_data: BaseUserSchema,
    db_session: AsyncSession = Depends(get_db),
    user_uuid_token: dict = Depends(get_current_user)
):
    repository = UserRepository(db_session=db_session)
    user = await repository.update_user(user_id=user_id, user_data=user_data)
    return UserResponse.model_validate(user)


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete a user by their ID.',
)
async def delete_user(
    user_id: UUID, 
    db_session: AsyncSession = Depends(get_db),
    user_uuid_token: dict = Depends(get_current_user)
):
    await UserRepository(db_session=db_session).delete_user(user_id=user_id)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        content='User deleted successfully.',
    )

@router.post(
        '/auth',
        summary="User authentication",
        description="""
            In this context the email will be used as username
            """,
        response_model=AccessToken
        )
async def auth(
    login_request_form: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db_session)
    token_data = await repository.authenticate(
        email=login_request_form.username,
        password=login_request_form.password
        )
    
    return token_data
