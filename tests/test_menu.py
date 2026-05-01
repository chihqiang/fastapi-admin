"""Tests for menu service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import Menu
from src.modules.sys.menu.repository import MenuRepository
from src.modules.sys.menu.schemas import (MenuCreate, MenuListRequest,
                                          MenuUpdate)
from src.modules.sys.menu.service import (create_menu, get_all_menus,
                                          get_menu_detail, get_menu_list,
                                          update_menu)


class TestMenuRepository:
    """Tests for MenuRepository."""

    @pytest_asyncio.fixture
    async def repo(self, db_session: AsyncSession) -> MenuRepository:
        """Create repository instance."""
        return MenuRepository(db_session)

    @pytest.mark.asyncio
    async def test_get_by_name(self, repo: MenuRepository, test_menu: Menu):
        """Test getting menu by name."""
        menu = await repo.get_by_name("Test Menu")

        assert menu is not None
        assert menu.name == "Test Menu"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, repo: MenuRepository):
        """Test getting non-existent menu by name."""
        menu = await repo.get_by_name("NonExistent Menu")

        assert menu is None

    @pytest.mark.asyncio
    async def test_list_all(self, repo: MenuRepository, test_menu: Menu):
        """Test listing all menus."""
        menus = await repo.list_all()

        assert len(menus) >= 1

    @pytest.mark.asyncio
    async def test_list_by_ids(self, repo: MenuRepository, test_menu: Menu):
        """Test listing menus by IDs."""
        menus = await repo.list_by_ids([test_menu.id])

        assert len(menus) == 1
        assert menus[0].id == test_menu.id


class TestMenuService:
    """Tests for menu service functions."""

    @pytest.mark.asyncio
    async def test_get_menu_list(self, db_session: AsyncSession, test_menu: Menu):
        """Test getting menu list."""
        request = MenuListRequest(page=1, size=10)
        result = await get_menu_list(request, db_session)

        assert result.total >= 1
        assert len(result.data) >= 1
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_get_menu_detail(self, db_session: AsyncSession, test_menu: Menu):
        """Test getting menu detail."""
        result = await get_menu_detail(test_menu.id, db_session)

        assert result.id == test_menu.id
        assert result.name == "Test Menu"

    @pytest.mark.asyncio
    async def test_get_menu_detail_not_found(self, db_session: AsyncSession):
        """Test getting non-existent menu detail."""
        with pytest.raises(Exception) as exc_info:
            await get_menu_detail(99999, db_session)
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
        result = await create_menu(menu_data, db_session)

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

        with pytest.raises(Exception) as exc_info:
            await create_menu(menu_data, db_session)
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
        result = await update_menu(test_menu.id, update_data, db_session)

        assert result.name == "Updated Menu"
        assert result.path == "/updated-path"
        assert result.sort == 10

    @pytest.mark.asyncio
    async def test_get_all_menus(self, db_session: AsyncSession, test_menu: Menu):
        """Test getting all menus."""
        result = await get_all_menus(db_session)

        assert len(result) >= 1
        assert any(m.name == "Test Menu" for m in result)
