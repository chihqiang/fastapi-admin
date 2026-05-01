from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import APIException
from src.models.auth import Role
from src.modules.sys.role.repository import RoleRepository
from src.modules.sys.role.schemas import (RoleCreate, RoleInfo,
                                          RoleListRequest, RoleListResponse,
                                          RoleUpdate)


async def get_role_list(request: RoleListRequest, db: AsyncSession) -> RoleListResponse:
    """获取角色列表"""
    repo = RoleRepository(db)

    # 获取总数
    filters = {}
    if request.id:
        filters["id"] = request.id
    # 注意：BaseRepository 的 count 目前只支持简单的等值过滤，模糊搜索需要手动处理
    if request.name:
        from sqlalchemy import func, select

        from src.models.auth import Role

        count_stmt = (
            select(func.count())
            .select_from(Role)
            .where(Role.name.like(f"%{request.name}%"))
        )
        if request.id:
            count_stmt = count_stmt.where(Role.id == request.id)
        total = (await db.execute(count_stmt)).scalar() or 0
    else:
        total = await repo.count(filters=filters)

    # 获取列表
    roles = await repo.list_with_menus(
        skip=request.offset, limit=request.size, role_id=request.id, name=request.name
    )

    # 自动化模型转 Schema
    role_list = [RoleInfo.model_validate(role) for role in roles]

    return RoleListResponse(
        data=role_list,
        total=total,
        page=request.page,
        size=request.size,
    )


async def get_role_detail(role_id: int, db: AsyncSession) -> RoleInfo:
    """获取角色详情"""
    repo = RoleRepository(db)
    role = await repo.get_with_menus(role_id)

    if not role:
        raise APIException(msg="角色不存在")

    return RoleInfo.model_validate(role)


async def create_role(role_data: RoleCreate, db: AsyncSession) -> RoleInfo:
    """创建角色"""
    repo = RoleRepository(db)

    # 检查名称
    if await repo.get_by_name(role_data.name):
        raise APIException(msg="角色名称已存在")

    # 创建基础角色（不立即 commit）
    role = Role(
        name=role_data.name,
        sort=role_data.sort,
        status=role_data.status,
        remark=role_data.remark,
    )
    db.add(role)

    # 关联菜单
    if role_data.menus:
        menu_ids = [menu.id for menu in role_data.menus]
        menus = await repo.get_menus_by_ids(menu_ids)
        role.menus = menus

    await db.commit()
    await db.refresh(role)

    return await get_role_detail(role.id, db)


async def update_role(
    role_id: int, role_data: RoleUpdate, db: AsyncSession
) -> RoleInfo:
    """更新角色"""
    repo = RoleRepository(db)
    role = await repo.get_with_menus(role_id)

    if not role:
        raise APIException(msg="角色不存在")

    # 检查名称
    if role_data.name != role.name:
        if await repo.get_by_name(role_data.name):
            raise APIException(msg="角色名称已存在")

    # 更新基础信息
    for field, value in role_data.model_dump(
        exclude={"menus"}, exclude_unset=True
    ).items():
        if hasattr(role, field):
            setattr(role, field, value)

    # 更新菜单（在同一事务中）
    if role_data.menus is not None:
        menu_ids = [menu.id for menu in role_data.menus]
        role.menus = await repo.get_menus_by_ids(menu_ids)

    await db.commit()
    await db.refresh(role)

    return await get_role_detail(role_id, db)


async def associate_role_menus(
    role_id: int, menu_ids: list[int], db: AsyncSession
) -> RoleInfo:
    """关联角色和菜单"""
    repo = RoleRepository(db)
    role = await repo.get_with_menus(role_id)
    if not role:
        raise APIException(msg="角色不存在")

    role.menus = await repo.get_menus_by_ids(menu_ids)
    await db.commit()
    await db.refresh(role)

    return RoleInfo.model_validate(role)


async def delete_role(role_id: int, db: AsyncSession) -> None:
    """删除角色"""
    from sqlalchemy import exists, select

    from src.models.auth import account_roles

    # 检查关联
    account_exists = await db.execute(
        select(exists().where(account_roles.c.role_id == role_id))
    )
    if account_exists.scalar():
        raise APIException(msg="角色关联了账号，不能删除")

    repo = RoleRepository(db)
    if not await repo.delete(role_id):
        raise APIException(msg="角色不存在")


async def get_all_roles(db: AsyncSession) -> list[RoleInfo]:
    """获取所有角色列表（不分页，用于下拉选择）"""
    repo = RoleRepository(db)
    roles = await repo.list_all()
    return [RoleInfo.model_validate(role) for role in roles]
