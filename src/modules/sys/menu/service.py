"""
菜单服务层

职责：
- 菜单 CRUD 操作
- 菜单树结构管理
- 业务逻辑处理
"""

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import APIException
from src.models.auth import Menu, role_menus
from src.modules.sys.menu.schemas import (MenuCreate, MenuInfo,
                                          MenuListRequest, MenuListResponse,
                                          MenuUpdate)


class MenuService:
    """菜单服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, request: MenuListRequest) -> MenuListResponse:
        """获取菜单列表"""
        filters = {}
        if request.id:
            filters["id"] = request.id
        if request.status is not None:
            filters["status"] = request.status

        if request.name:
            count_stmt = (
                select(func.count())
                .select_from(Menu)
                .where(Menu.name.like(f"%{request.name}%"))
            )
            if request.id:
                count_stmt = count_stmt.where(Menu.id == request.id)
            if request.status is not None:
                count_stmt = count_stmt.where(Menu.status == request.status)
            total = (await self.db.execute(count_stmt)).scalar() or 0
        else:
            total = await self._count(filters=filters)

        if request.name:
            stmt = select(Menu).where(Menu.name.like(f"%{request.name}%"))
            if request.id:
                stmt = stmt.where(Menu.id == request.id)
            if request.status is not None:
                stmt = stmt.where(Menu.status == request.status)
            stmt = stmt.offset(request.offset).limit(request.size)
            menus = (await self.db.execute(stmt)).scalars().all()
        else:
            menus = await self._list(
                skip=request.offset, limit=request.size, filters=filters
            )

        menu_list = [MenuInfo.model_validate(menu) for menu in menus]

        return MenuListResponse(
            data=menu_list,
            total=total,
            page=request.page,
            size=request.size,
        )

    async def get_all(self) -> list[MenuInfo]:
        """获取所有菜单"""
        menus = await self._list_all()
        return [MenuInfo.model_validate(menu) for menu in menus]

    async def get_detail(self, menu_id: int) -> MenuInfo:
        """获取菜单详情"""
        menu = await self._get(menu_id)
        if not menu:
            raise APIException(msg="菜单不存在")

        return MenuInfo.model_validate(menu)

    async def create(self, menu_data: MenuCreate) -> MenuInfo:
        """创建菜单"""
        if await self._get_by_name(menu_data.name):
            raise APIException(msg="菜单名称已存在")

        if menu_data.pid:
            if not await self._get(menu_data.pid):
                raise APIException(msg="父菜单不存在")

        menu_dict = menu_data.model_dump()
        if "pid" in menu_dict and menu_dict["pid"] is None:
            menu_dict["pid"] = 0

        menu = await self._create(menu_dict)
        return MenuInfo.model_validate(menu)

    async def update(self, menu_id: int, menu_data: MenuUpdate) -> MenuInfo:
        """更新菜单"""
        menu = await self._get(menu_id)
        if not menu:
            raise APIException(msg="菜单不存在")

        if menu_data.name != menu.name:
            if await self._get_by_name(menu_data.name):
                raise APIException(msg="菜单名称已存在")

        if menu_data.pid:
            if not await self._get(menu_data.pid):
                raise APIException(msg="父菜单不存在")

        update_data = menu_data.model_dump(exclude_unset=True)
        if "pid" in update_data and update_data["pid"] is None:
            update_data["pid"] = 0

        await self._update(menu, update_data)
        return MenuInfo.model_validate(menu)

    async def delete(self, menu_id: int) -> None:
        """删除菜单"""
        child_exists = await self.db.execute(
            select(exists().where(Menu.pid == menu_id))
        )
        if child_exists.scalar():
            raise APIException(msg="存在子菜单，无法删除")

        role_exists = await self.db.execute(
            select(exists().where(role_menus.c.menu_id == menu_id))
        )
        if role_exists.scalar():
            raise APIException(msg="菜单关联了角色，不能删除")

        if not await self._delete(menu_id):
            raise APIException(msg="菜单不存在")

    # ==================== 私有方法 ====================

    async def _get(self, menu_id: int) -> Menu | None:
        """根据ID获取菜单"""
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _get_by_name(self, name: str) -> Menu | None:
        """根据名称获取菜单"""
        stmt = select(Menu).where(Menu.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, object] | None = None
    ) -> list[Menu]:
        """获取菜单列表"""
        stmt = select(Menu)
        if filters:
            for field, value in filters.items():
                if hasattr(Menu, field):
                    stmt = stmt.where(getattr(Menu, field) == value)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _list_all(
        self, name: str | None = None, status: bool | None = None
    ) -> list[Menu]:
        """获取所有菜单（不分页）"""
        stmt = select(Menu).order_by(Menu.sort.asc())
        if name:
            stmt = stmt.where(Menu.name.like(f"%{name}%"))
        if status is not None:
            stmt = stmt.where(Menu.status == status)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _count(self, filters: dict[str, object] | None = None) -> int:
        """获取记录总数"""
        stmt = select(func.count()).select_from(Menu)
        if filters:
            for field, value in filters.items():
                if hasattr(Menu, field):
                    stmt = stmt.where(getattr(Menu, field) == value)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def _create(self, obj_in: dict[str, object]) -> Menu:
        """创建菜单"""
        menu = Menu(**obj_in)
        self.db.add(menu)
        await self.db.commit()
        await self.db.refresh(menu)
        return menu

    async def _update(self, db_obj: Menu, obj_in: dict[str, object]) -> Menu:
        """更新菜单"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _delete(self, menu_id: int) -> bool:
        """删除菜单"""
        menu = await self._get(menu_id)
        if menu:
            await self.db.delete(menu)
            await self.db.commit()
            return True
        return False
