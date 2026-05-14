"""Tests for role service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import Menu, Role
from src.modules.sys.role.schemas import MenuId, RoleCreate, RoleListRequest, RoleUpdate
from src.modules.sys.role.service import RoleService


class TestRoleService:
    """Tests for role service functions."""

    @pytest.mark.asyncio
    async def test_get_role_list(self, db_session: AsyncSession, test_role: Role):
        """Test getting role list."""
        request = RoleListRequest(page=1, size=10)
        service = RoleService(db_session)
        result = await service.get_list(request)

        assert result.total >= 1
        assert len(result.data) >= 1
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_get_role_detail(self, db_session: AsyncSession, test_role: Role):
        """Test getting role detail."""
        service = RoleService(db_session)
        result = await service.get_detail(test_role.id)

        assert result.id == test_role.id
        assert result.name == "Test Role"

    @pytest.mark.asyncio
    async def test_get_role_detail_not_found(self, db_session: AsyncSession):
        """Test getting non-existent role detail."""
        service = RoleService(db_session)
        with pytest.raises(Exception) as exc_info:
            await service.get_detail(99999)
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
        service = RoleService(db_session)
        result = await service.create(role_data)

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
        service = RoleService(db_session)
        with pytest.raises(Exception) as exc_info:
            await service.create(role_data)
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
        service = RoleService(db_session)
        result = await service.update(test_role.id, update_data)

        assert result.name == "Updated Role"
        assert result.sort == 5
        assert result.remark == "Updated remark"

    @pytest.mark.asyncio
    async def test_associate_role_menus(
        self, db_session: AsyncSession, test_role: Role, test_menu: Menu
    ):
        """Test associating role with menus."""
        role_data = RoleUpdate(
            id=test_role.id, name=test_role.name, menus=[MenuId(id=test_menu.id)]
        )
        service = RoleService(db_session)
        result = await service.update(test_role.id, role_data)

        assert len(result.menus) >= 1

    @pytest.mark.asyncio
    async def test_get_all_roles(self, db_session: AsyncSession, test_role: Role):
        """Test getting all roles."""
        service = RoleService(db_session)
        result = await service.get_all()

        assert len(result) >= 1
        assert any(r.name == "Test Role" for r in result)
