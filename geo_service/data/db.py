import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/geo"
)


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://geo_user:geo_pass@postgis_db:5432/geo_test",
)


test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
async_test_session = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)
