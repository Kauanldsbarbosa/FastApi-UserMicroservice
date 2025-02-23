from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import get_config

load_dotenv()

DATABASE_URL = get_config().DATABASE_URL

if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace(
        'postgresql://', 'postgresql+asyncpg://'
    )

elif DATABASE_URL and DATABASE_URL.startswith('sqlite:///'):
    DATABASE_URL = DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
)


Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with Session() as session:
        try:
            yield session
        finally:
            await session.close()
