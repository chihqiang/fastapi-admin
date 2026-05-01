from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.models.auth import Menu


class MenuRepository(BaseRepository[Menu]):
    def __init__(self, db: AsyncSession):
        super().__init__(Menu, db)

    async def get_by_name(self, name: str) -> Menu | None:
        """根据名称获取菜单"""
        stmt = select(self.model).where(self.model.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_ids(self, ids: list[int]) -> list[Menu]:
        """根据 ID 列表获取菜单"""
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_all(
        self, name: str | None = None, status: bool | None = None
    ) -> list[Menu]:
        """获取所有菜单（不分页，通常用于树形展示）"""
        stmt = select(self.model).order_by(self.model.sort.asc())
        if name:
            stmt = stmt.where(self.model.name.like(f"%{name}%"))
        if status is not None:
            stmt = stmt.where(self.model.status == status)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
