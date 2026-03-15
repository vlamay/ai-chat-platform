import pytest
import pytest_asyncio
import os
import asyncio
import sys

# Mock the database engine before importing app modules
os.environ['DATABASE_URL'] = "sqlite+aiosqlite:///:memory:"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from httpx import AsyncClient, ASGITransport
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# Import app modules that need the database
from app.core.database import Base, get_db
from app.main import app
from app.models import User, Chat, Message
from app.services.auth import create_tokens


# Override database URL for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Initialize cache for tests
FastAPICache.init(InMemoryBackend(), prefix="test-cache")


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine with in-memory SQLite"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine):
    """Create test database session"""
    TestSessionLocal = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def override_get_db(test_db_session):
    """Override get_db dependency for tests"""
    async def _override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_db):
    """Create async test client"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(test_db_session):
    """Create a test user"""
    from app.services.auth import create_user

    user = await create_user(test_db_session, "test@example.com", "Test User", "password123")
    return user


@pytest_asyncio.fixture
async def test_user_tokens(test_user):
    """Generate tokens for test user"""
    access_token, refresh_token = create_tokens(test_user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": test_user.id,
    }


@pytest_asyncio.fixture
async def test_chat(test_db_session, test_user):
    """Create a test chat"""
    chat = Chat(user_id=test_user.id, title="Test Chat", model="claude-3-sonnet-20240229")
    test_db_session.add(chat)
    await test_db_session.commit()
    await test_db_session.refresh(chat)
    return chat


@pytest_asyncio.fixture
async def test_message(test_db_session, test_chat):
    """Create a test message"""
    message = Message(chat_id=test_chat.id, role="user", content="Hello!")
    test_db_session.add(message)
    await test_db_session.commit()
    await test_db_session.refresh(message)
    return message


