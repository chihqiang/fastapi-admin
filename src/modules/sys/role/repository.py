from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.repository import BaseRepository
from src.models.auth import Menu, Role


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Role | None:
        """根据名称获取角色"""
        stmt = select(self.model).where(self.model.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_with_menus(self, role_id: int) -> Role | None:
        """获取带菜单的角色详情"""
        stmt = (
            select(self.model)
            .options(joinedload(self.model.menus))
            .where(self.model.id == role_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def list_with_menus(
        self,
        skip: int = 0,
        limit: int = 10,
        role_id: int | None = None,
        name: str | None = None,
    ) -> list[Role]:
        """分页获取带菜单的角色列表"""
        stmt = select(self.model).options(selectinload(self.model.menus))
        if role_id:
            stmt = stmt.where(self.model.id == role_id)
        if name:
            stmt = stmt.where(self.model.name.like(f"%{name}%"))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def get_menus_by_ids(self, menu_ids: list[int]) -> list[Menu]:
        """根据 ID 列表获取菜单"""
        stmt = select(Menu).where(Menu.id.in_(menu_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[Role]:
        """获取所有角色（不分页）"""
        stmt = select(self.model).options(selectinload(self.model.menus))
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()
