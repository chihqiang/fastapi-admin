"""Tests for account service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import Account, Role
from src.modules.sys.account.schemas import (
    AccountCreate,
    AccountListRequest,
    AccountUpdate,
)
from src.modules.sys.account.service import AccountService


class TestAccountService:
    """Tests for account service functions."""

    @pytest.mark.asyncio
    async def test_get_account_list(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test getting account list."""
        request = AccountListRequest(page=1, size=10)
        service = AccountService(db_session)
        result = await service.get_list(request)

        assert result.total >= 1
        assert len(result.data) >= 1
        assert result.page == 1
        assert result.size == 10

    @pytest.mark.asyncio
    async def test_get_account_detail(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test getting account detail."""
        service = AccountService(db_session)
        result = await service.get_detail(test_account.id)

        assert result.id == test_account.id
        assert result.email == "test@example.com"
        assert result.name == "Test User"

    @pytest.mark.asyncio
    async def test_get_account_detail_not_found(self, db_session: AsyncSession):
        """Test getting non-existent account detail."""
        service = AccountService(db_session)
        with pytest.raises(Exception) as exc_info:
            await service.get_detail(99999)
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
        service = AccountService(db_session)
        result = await service.create(account_data)

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
            roles=[],
        )
        service = AccountService(db_session)
        with pytest.raises(Exception) as exc_info:
            await service.create(account_data)
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
        service = AccountService(db_session)
        result = await service.update(test_account.id, update_data)

        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_account(
        self, db_session: AsyncSession, test_account: Account
    ):
        """Test deleting an account — uses _delete to avoid self-delete check."""
        service = AccountService(db_session)
        # 使用内部方法绕过"不能删除自己"的校验
        deleted = await service._delete(test_account.id)
        assert deleted is True
