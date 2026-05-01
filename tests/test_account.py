"""Tests for account service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import Account, Role
from src.modules.sys.account.repository import AccountRepository
from src.modules.sys.account.schemas import (AccountCreate, AccountListRequest,
                                             AccountUpdate)
from src.modules.sys.account.service import (create_account,
                                             get_account_detail,
                                             get_account_list, update_account)


class TestAccountRepository:
    """Tests for AccountRepository."""

    @pytest_asyncio.fixture
    async def repo(self, db_session: AsyncSession) -> AccountRepository:
        """Create repository instance."""
        return AccountRepository(db_session)

    @pytest.mark.asyncio
    async def test_create_account(self, repo: AccountRepository):
        """Test creating an account."""
        account_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "hashed_password_123",  # password 字段是 NOT NULL
            "status": True,
        }
        account = await repo.create(account_data)
        await repo.db.commit()
        await repo.db.refresh(account)

        assert account.id is not None
        assert account.name == "New User"
        assert account.email == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email(self, repo: AccountRepository, test_account: Account):
        """Test getting account by email."""
        account = await repo.get_by_email("test@example.com")

        assert account is not None
        assert account.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, repo: AccountRepository):
        """Test getting non-existent account by email."""
        account = await repo.get_by_email("nonexistent@example.com")

        assert account is None

    @pytest.mark.asyncio
    async def test_list_accounts(self, repo: AccountRepository, test_account: Account):
        """Test listing accounts."""
        accounts = await repo.list(skip=0, limit=10)

        assert len(accounts) >= 1
        assert any(a.email == "test@example.com" for a in accounts)

    @pytest.mark.asyncio
    async def test_delete_account(self, repo: AccountRepository, test_account: Account):
        """Test deleting an account."""
        deleted = await repo.delete(test_account.id)

        assert deleted is not None
        assert deleted.id == test_account.id


class TestAccountService:
    """Tests for account service functions."""

    @pytest.mark.asyncio
    async def test_get_account_list(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test getting account list."""
        request = AccountListRequest(page=1, size=10)
        result = await get_account_list(request, db_session)

        assert result.total >= 1
        assert len(result.data) >= 1
        assert result.page == 1
        assert result.size == 10

    @pytest.mark.asyncio
    async def test_get_account_detail(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test getting account detail."""
        result = await get_account_detail(test_account.id, db_session)

        assert result.id == test_account.id
        assert result.email == "test@example.com"
        assert result.name == "Test User"

    @pytest.mark.asyncio
    async def test_get_account_detail_not_found(self, db_session: AsyncSession):
        """Test getting non-existent account detail."""
        with pytest.raises(Exception) as exc_info:
            await get_account_detail(99999, db_session)
        assert "账号不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_account(self, db_session: AsyncSession, test_role: Role):
        """Test creating a new account."""
        account_data = AccountCreate(
            name="New User",
            email="newuser@example.com",
            password="password123",
            status=True,
            roles=[],
        )
        result = await create_account(account_data, db_session)

        assert result.id is not None
        assert result.name == "New User"
        assert result.email == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_create_account_duplicate_email(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test creating account with duplicate email."""
        account_data = AccountCreate(
            name="Another User",
            email="test@example.com",  # Duplicate email
            password="password123",
            status=True,
        )

        with pytest.raises(Exception) as exc_info:
            await create_account(account_data, db_session)
        assert "邮箱已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_account(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test updating an account."""
        update_data = AccountUpdate(
            id=test_account.id,
            name="Updated Name",
            email=test_account.email,
            status=True,
        )
        result = await update_account(test_account.id, update_data, db_session)

        assert result.name == "Updated Name"
