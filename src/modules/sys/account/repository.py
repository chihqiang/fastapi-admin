from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.repository import BaseRepository
from src.models.auth import Account, Role


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: AsyncSession):
        super().__init__(Account, db)

    async def get_by_email(self, email: str) -> Optional[Account]:
        """根据邮箱获取账号"""
        stmt = select(self.model).where(self.model.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_with_roles(self, account_id: int) -> Optional[Account]:
        """获取带角色的账号详情"""
        stmt = (
            select(self.model)
            .options(joinedload(self.model.roles))
            .where(self.model.id == account_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def list_with_roles(
        self, skip: int = 0, limit: int = 10, account_id: Optional[int] = None
    ) -> List[Account]:
        """分页获取带角色的账号列表"""
        stmt = select(self.model).options(selectinload(self.model.roles))
        if account_id:
            stmt = stmt.where(self.model.id == account_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def get_roles_by_ids(self, role_ids: List[int]) -> List[Role]:
        """根据 ID 列表获取角色"""
        stmt = select(Role).where(Role.id.in_(role_ids))
        result = await self.db.execute(stmt)
        return result.scalars().all()
