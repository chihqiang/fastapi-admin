"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base
from src.models.auth import Account, Menu, Role


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create in-memory database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()

    try:
        yield async_session
    finally:
        await async_session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def test_account(db_session: AsyncSession) -> Account:
    """Create a test account."""
    account = Account(
        name="Test User",
        email="test@example.com",
        status=True,
    )
    account.set_password("test123")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession) -> Role:
    """Create a test role."""
    role = Role(
        name="Test Role",
        sort=0,
        status=True,
        remark="Test role for unit testing",
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def test_menu(db_session: AsyncSession) -> Menu:
    """Create a test menu."""
    menu = Menu(
        name="Test Menu",
        menu_type=2,
        path="/test",
        component="test/index",
        sort=0,
        status=True,
    )
    db_session.add(menu)
    await db_session.commit()
    await db_session.refresh(menu)
    return menu
