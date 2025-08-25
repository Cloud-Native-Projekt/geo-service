import asyncio

import asyncpg
import pytest

from geo_service.data.db import async_test_session, test_engine
from geo_service.data.geo_models import Base


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    # damit pytest-asyncio asyncio Eventloop nutzt
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    """Creates the test database schema."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Optional: Tabellen löschen nach Tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session():
    """Creates a new database session for a test."""
    async with async_test_session() as session:
        async with session.begin():
            # Tabellen leeren, damit Tests deterministisch sind
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(f"TRUNCATE TABLE {table.name} CASCADE;")
        yield session
        await session.commit()
