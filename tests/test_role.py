"""Tests for role service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import Menu, Role
from src.modules.sys.role.repository import RoleRepository
from src.modules.sys.role.schemas import (MenuId, RoleCreate, RoleListRequest,
                                          RoleUpdate)
from src.modules.sys.role.service import (create_role, get_all_roles,
                                          get_role_detail, get_role_list,
                                          update_role)


class TestRoleRepository:
    """Tests for RoleRepository."""

    @pytest_asyncio.fixture
    async def repo(self, db_session: AsyncSession) -> RoleRepository:
        """Create repository instance."""
        return RoleRepository(db_session)

    @pytest.mark.asyncio
    async def test_get_by_name(self, repo: RoleRepository, test_role: Role):
        """Test getting role by name."""
        role = await repo.get_by_name("Test Role")

        assert role is not None
        assert role.name == "Test Role"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, repo: RoleRepository):
        """Test getting non-existent role by name."""
        role = await repo.get_by_name("NonExistent Role")

        assert role is None

    @pytest.mark.asyncio
    async def test_list_all(self, repo: RoleRepository, test_role: Role):
        """Test listing all roles."""
        roles = await repo.list_all()

        assert len(roles) >= 1

    @pytest.mark.asyncio
    async def test_get_menus_by_ids(self, repo: RoleRepository, test_menu: Menu):
        """Test getting menus by IDs."""
        menus = await repo.get_menus_by_ids([test_menu.id])

        assert len(menus) == 1
        assert menus[0].id == test_menu.id


class TestRoleService:
    """Tests for role service functions."""

    @pytest.mark.asyncio
    async def test_get_role_list(self, db_session: AsyncSession, test_role: Role):
        """Test getting role list."""
        request = RoleListRequest(page=1, size=10)
        result = await get_role_list(request, db_session)

        assert result.total >= 1
        assert len(result.data) >= 1
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_get_role_detail(self, db_session: AsyncSession, test_role: Role):
        """Test getting role detail."""
        result = await get_role_detail(test_role.id, db_session)

        assert result.id == test_role.id
        assert result.name == "Test Role"

    @pytest.mark.asyncio
    async def test_get_role_detail_not_found(self, db_session: AsyncSession):
        """Test getting non-existent role detail."""
        with pytest.raises(Exception) as exc_info:
            await get_role_detail(99999, db_session)
        assert "角色不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_role(self, db_session: AsyncSession):
        """Test creating a new role."""
        role_data = RoleCreate(
            name="New Role",
            sort=1,
            status=True,
            remark="A new test role",
            menus=[],
        )
        result = await create_role(role_data, db_session)

        assert result.id is not None
        assert result.name == "New Role"
        assert result.remark == "A new test role"

    @pytest.mark.asyncio
    async def test_create_role_duplicate_name(
        self, db_session: AsyncSession, test_role: Role
    ):
        """Test creating role with duplicate name."""
        role_data = RoleCreate(
            name="Test Role",  # Duplicate name
            sort=1,
            status=True,
            menus=[],
        )

        with pytest.raises(Exception) as exc_info:
            await create_role(role_data, db_session)
        assert "角色名称已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_role(self, db_session: AsyncSession, test_role: Role):
        """Test updating a role."""
        update_data = RoleUpdate(
            id=test_role.id,
            name="Updated Role",
            sort=5,
            status=True,
            remark="Updated remark",
            menus=None,
        )
        result = await update_role(test_role.id, update_data, db_session)

        assert result.name == "Updated Role"
        assert result.sort == 5
        assert result.remark == "Updated remark"

    @pytest.mark.asyncio
    async def test_associate_role_menus(
        self, db_session: AsyncSession, test_role: Role, test_menu: Menu
    ):
        """Test associating role with menus."""
        # 使用 update_role 函数来测试角色菜单关联
        from src.modules.sys.role.service import update_role

        role_data = RoleUpdate(
            id=test_role.id, name=test_role.name, menus=[MenuId(id=test_menu.id)]
        )
        result = await update_role(test_role.id, role_data, db_session)

        # 验证角色已关联菜单
        assert len(result.menus) >= 1

    @pytest.mark.asyncio
    async def test_get_all_roles(self, db_session: AsyncSession, test_role: Role):
        """Test getting all roles."""
        result = await get_all_roles(db_session)

        assert len(result) >= 1
        assert any(r.name == "Test Role" for r in result)
