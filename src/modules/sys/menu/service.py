from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import APIException
from src.modules.sys.menu.repository import MenuRepository
from src.modules.sys.menu.schemas import (MenuCreate, MenuInfo,
                                          MenuListRequest, MenuListResponse,
                                          MenuUpdate)


async def get_menu_list(request: MenuListRequest, db: AsyncSession) -> MenuListResponse:
    """获取菜单列表"""
    repo = MenuRepository(db)

    # 获取总数
    filters = {}
    if request.id:
        filters["id"] = request.id
    if request.status is not None:
        filters["status"] = request.status

    if request.name:
        from sqlalchemy import func, select

        from src.models.auth import Menu

        count_stmt = (
            select(func.count())
            .select_from(Menu)
            .where(Menu.name.like(f"%{request.name}%"))
        )
        if request.id:
            count_stmt = count_stmt.where(Menu.id == request.id)
        if request.status is not None:
            count_stmt = count_stmt.where(Menu.status == request.status)
        total = (await db.execute(count_stmt)).scalar() or 0
    else:
        total = await repo.count(filters=filters)

    # 获取列表
    menus = await repo.list(skip=request.offset, limit=request.size, filters=filters)
    if request.name:
        # 如果有模糊搜索，需要特殊处理 list 方法或手动过滤
        from sqlalchemy import select

        from src.models.auth import Menu

        stmt = select(Menu).where(Menu.name.like(f"%{request.name}%"))
        if request.id:
            stmt = stmt.where(Menu.id == request.id)
        if request.status is not None:
            stmt = stmt.where(Menu.status == request.status)
        stmt = stmt.offset(request.offset).limit(request.size)
        menus = (await db.execute(stmt)).scalars().all()

    # 自动化模型转 Schema
    menu_list = [MenuInfo.model_validate(menu) for menu in menus]

    return MenuListResponse(
        data=menu_list,
        total=total,
        page=request.page,
        size=request.size,
    )


async def get_all_menus(db: AsyncSession) -> list[MenuInfo]:
    """获取所有菜单列表（用于下拉选择）"""
    repo = MenuRepository(db)
    menus = await repo.list_all()
    return [MenuInfo.model_validate(menu) for menu in menus]


async def get_menu_detail(menu_id: int, db: AsyncSession) -> MenuInfo:
    """获取菜单详情"""
    repo = MenuRepository(db)
    menu = await repo.get(menu_id)

    if not menu:
        raise APIException(msg="菜单不存在")

    return MenuInfo.model_validate(menu)


async def create_menu(menu_data: MenuCreate, db: AsyncSession) -> MenuInfo:
    """创建菜单"""
    repo = MenuRepository(db)

    # 检查名称
    if await repo.get_by_name(menu_data.name):
        raise APIException(msg="菜单名称已存在")

    # 检查父菜单
    if menu_data.pid:
        if not await repo.get(menu_data.pid):
            raise APIException(msg="父菜单不存在")

    # 创建菜单
    menu_dict = menu_data.model_dump()
    if "pid" in menu_dict and menu_dict["pid"] is None:
        menu_dict["pid"] = 0

    menu = await repo.create(menu_dict)
    return MenuInfo.model_validate(menu)


async def update_menu(
    menu_id: int, menu_data: MenuUpdate, db: AsyncSession
) -> MenuInfo:
    """更新菜单"""
    repo = MenuRepository(db)
    menu = await repo.get(menu_id)

    if not menu:
        raise APIException(msg="菜单不存在")

    # 检查名称
    if menu_data.name != menu.name:
        if await repo.get_by_name(menu_data.name):
            raise APIException(msg="菜单名称已存在")

    # 检查父菜单
    if menu_data.pid:
        if not await repo.get(menu_data.pid):
            raise APIException(msg="父菜单不存在")

    # 更新信息
    update_data = menu_data.model_dump(exclude_unset=True)
    if "pid" in update_data and update_data["pid"] is None:
        update_data["pid"] = 0

    await repo.update(menu, update_data)
    return MenuInfo.model_validate(menu)


async def delete_menu(menu_id: int, db: AsyncSession) -> None:
    """删除菜单"""
    repo = MenuRepository(db)

    # 检查子菜单
    from sqlalchemy import exists, select

    from src.models.auth import Menu, role_menus

    child_exists = await db.execute(select(exists().where(Menu.pid == menu_id)))
    if child_exists.scalar():
        raise APIException(msg="存在子菜单，无法删除")

    # 检查关联
    role_exists = await db.execute(
        select(exists().where(role_menus.c.menu_id == menu_id))
    )
    if role_exists.scalar():
        raise APIException(msg="菜单关联了角色，不能删除")

    if not await repo.delete(menu_id):
        raise APIException(msg="菜单不存在")
