"""Tests for menu service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import Menu
from src.modules.sys.menu.schemas import MenuCreate, MenuListRequest, MenuUpdate
from src.modules.sys.menu.service import MenuService


class TestMenuService:
    """Tests for menu service functions."""

    @pytest.mark.asyncio
    async def test_get_menu_list(self, db_session: AsyncSession, test_menu: Menu):
        """Test getting menu list."""
        request = MenuListRequest(page=1, size=10)
        service = MenuService(db_session)
        result = await service.get_list(request)

        assert result.total >= 1
        assert len(result.data) >= 1
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_get_menu_detail(self, db_session: AsyncSession, test_menu: Menu):
        """Test getting menu detail."""
        service = MenuService(db_session)
        result = await service.get_detail(test_menu.id)

        assert result.id == test_menu.id
        assert result.name == "Test Menu"

    @pytest.mark.asyncio
    async def test_get_menu_detail_not_found(self, db_session: AsyncSession):
        """Test getting non-existent menu detail."""
        service = MenuService(db_session)
        with pytest.raises(Exception) as exc_info:
            await service.get_detail(99999)
        assert "菜单不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_menu(self, db_session: AsyncSession):
        """Test creating a new menu."""
        menu_data = MenuCreate(
            name="New Menu",
            menu_type=2,
            path="/new-menu",
            component="new-menu/index",
            sort=1,
            status=True,
        )
        service = MenuService(db_session)
        result = await service.create(menu_data)

        assert result.id is not None
        assert result.name == "New Menu"
        assert result.path == "/new-menu"

    @pytest.mark.asyncio
    async def test_create_menu_duplicate_name(
        self, db_session: AsyncSession, test_menu: Menu
    ):
        """Test creating menu with duplicate name."""
        menu_data = MenuCreate(
            name="Test Menu",  # Duplicate name
            menu_type=2,
            path="/another-path",
        )
        service = MenuService(db_session)
        with pytest.raises(Exception) as exc_info:
            await service.create(menu_data)
        assert "菜单名称已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_menu(self, db_session: AsyncSession, test_menu: Menu):
        """Test updating a menu."""
        update_data = MenuUpdate(
            id=test_menu.id,
            name="Updated Menu",
            menu_type=test_menu.menu_type,
            path="/updated-path",
            component="updated/index",
            sort=10,
            status=True,
        )
        service = MenuService(db_session)
        result = await service.update(test_menu.id, update_data)

        assert result.name == "Updated Menu"
        assert result.path == "/updated-path"
        assert result.sort == 10

    @pytest.mark.asyncio
    async def test_get_all_menus(self, db_session: AsyncSession, test_menu: Menu):
        """Test getting all menus."""
        service = MenuService(db_session)
        result = await service.get_all()

        assert len(result) >= 1
        assert any(m.name == "Test Menu" for m in result)
