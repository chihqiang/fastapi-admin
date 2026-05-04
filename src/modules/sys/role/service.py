"""
角色服务层

职责：
- 角色 CRUD 操作
- 角色菜单关联管理
- 业务逻辑处理
"""

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.exception import APIException
from src.models.auth import Menu, Role, account_roles
from src.modules.sys.role.schemas import (
    RoleCreate,
    RoleInfo,
    RoleListRequest,
    RoleListResponse,
    RoleUpdate,
)


class RoleService:
    """角色服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, request: RoleListRequest) -> RoleListResponse:
        """获取角色列表"""
        filters = {}
        if request.id:
            filters["id"] = request.id

        if request.name:
            count_stmt = (
                select(func.count())
                .select_from(Role)
                .where(Role.name.like(f"%{request.name}%"))
            )
            if request.id:
                count_stmt = count_stmt.where(Role.id == request.id)
            total = (await self.db.execute(count_stmt)).scalar() or 0
        else:
            total = await self._count(filters=filters)

        roles = await self._list_with_menus(
            skip=request.offset, limit=request.size, role_id=request.id, name=request.name
        )

        role_list = [RoleInfo.model_validate(role) for role in roles]

        return RoleListResponse(
            data=role_list,
            total=total,
            page=request.page,
            size=request.size,
        )

    async def get_detail(self, role_id: int) -> RoleInfo:
        """获取角色详情"""
        role = await self._get_with_menus(role_id)
        if not role:
            raise APIException(msg="角色不存在")

        return RoleInfo.model_validate(role)

    async def create(self, role_data: RoleCreate) -> RoleInfo:
        """创建角色"""
        if await self._get_by_name(role_data.name):
            raise APIException(msg="角色名称已存在")

        role = Role(
            name=role_data.name,
            sort=role_data.sort,
            status=role_data.status,
            remark=role_data.remark,
        )
        self.db.add(role)

        if role_data.menus:
            menu_ids = [menu.id for menu in role_data.menus]
            menus = await self._get_menus_by_ids(menu_ids)
            role.menus = menus

        await self.db.commit()
        await self.db.refresh(role)

        return await self.get_detail(role.id)

    async def update(self, role_id: int, role_data: RoleUpdate) -> RoleInfo:
        """更新角色"""
        role = await self._get_with_menus(role_id)
        if not role:
            raise APIException(msg="角色不存在")

        if role_data.name != role.name:
            if await self._get_by_name(role_data.name):
                raise APIException(msg="角色名称已存在")

        for field, value in role_data.model_dump(
            exclude={"menus"}, exclude_unset=True
        ).items():
            if hasattr(role, field):
                setattr(role, field, value)

        if role_data.menus is not None:
            menu_ids = [menu.id for menu in role_data.menus]
            role.menus = await self._get_menus_by_ids(menu_ids)

        await self.db.commit()
        await self.db.refresh(role)

        return await self.get_detail(role_id)

    async def delete(self, role_id: int) -> None:
        """删除角色"""
        account_exists = await self.db.execute(
            select(exists().where(account_roles.c.role_id == role_id))
        )
        if account_exists.scalar():
            raise APIException(msg="角色关联了账号，不能删除")

        if not await self._delete(role_id):
            raise APIException(msg="角色不存在")

    async def get_all(self) -> list[RoleInfo]:
        """获取所有角色（不分页）"""
        roles = await self._list_all()
        return [RoleInfo.model_validate(role) for role in roles]

    async def associate_menus(self, role_id: int, menu_ids: list[int]) -> RoleInfo:
        """关联角色和菜单"""
        role = await self._get_with_menus(role_id)
        if not role:
            raise APIException(msg="角色不存在")

        role.menus = await self._get_menus_by_ids(menu_ids)
        await self.db.commit()
        await self.db.refresh(role)

        return RoleInfo.model_validate(role)

    # ==================== 私有方法 ====================

    async def _get_by_name(self, name: str) -> Role | None:
        """根据名称获取角色"""
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _get_with_menus(self, role_id: int) -> Role | None:
        """获取带菜单的角色详情"""
        stmt = (
            select(Role)
            .options(joinedload(Role.menus))
            .where(Role.id == role_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def _list_with_menus(
        self,
        skip: int = 0,
        limit: int = 10,
        role_id: int | None = None,
        name: str | None = None,
    ) -> list[Role]:
        """分页获取带菜单的角色列表"""
        stmt = select(Role).options(selectinload(Role.menus))
        if role_id:
            stmt = stmt.where(Role.id == role_id)
        if name:
            stmt = stmt.where(Role.name.like(f"%{name}%"))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def _list_all(self) -> list[Role]:
        """获取所有角色（不分页）"""
        stmt = select(Role).options(selectinload(Role.menus))
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def _count(self, filters: dict[str, object] | None = None) -> int:
        """获取记录总数"""
        stmt = select(func.count()).select_from(Role)
        if filters:
            for field, value in filters.items():
                if hasattr(Role, field):
                    stmt = stmt.where(getattr(Role, field) == value)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def _get_menus_by_ids(self, menu_ids: list[int]) -> list[Menu]:
        """根据ID列表获取菜单"""
        stmt = select(Menu).where(Menu.id.in_(menu_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _delete(self, role_id: int) -> bool:
        """删除角色"""
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db.execute(stmt)
        role = result.scalars().first()
        if role:
            await self.db.delete(role)
            await self.db.commit()
            return True
        return False
