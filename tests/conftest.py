import asyncio
import os
from datetime import date

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.system.database.base import Base
from app.system.database.connection import Session, engine, get_db
from app.user.models import User
from app.system.security.security import get_password_hash
from app.user.utils.decode_user_token import get_current_user

os.environ['ENVIRONMENT'] = 'test'

load_dotenv()


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session():
    async with Session() as session:
        try:
            yield session
        except Exception as e:
            print(f'Erro na sessão de teste: {e}')
        finally:
            try:
                await session.rollback()
            except Exception:
                pass
            await session.close()


def override_get_current_user():
    return {"user_id": "test_user"}

app.dependency_overrides[get_current_user] = override_get_current_user
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://localhost:8000'
    ) as c:
        yield c


@pytest_asyncio.fixture
async def create_user(db_session: AsyncSession):
    user = User(
        email='validuser@example.com',
        first_name='John',
        last_name='Doe',
        date_of_birth=date(1995, 5, 20),
        password='SecurePass!',
    )
    user.password = get_password_hash(user.password)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    try:
        await db_session.delete(user)
        await db_session.commit()
    except Exception as e:
        print(f'Erro ao deletar usuário de teste: {e}')


@pytest.fixture
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = Session()
    yield session

    await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db(setup_db):
    def _get_test_db():
        yield setup_db

    return _get_test_db


@pytest.fixture(autouse=True)
def override_dependency(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
