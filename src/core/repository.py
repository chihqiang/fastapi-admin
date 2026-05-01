from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model: type[ModelType] = model
        self.db: AsyncSession = db

    async def get(self, id: int) -> ModelType | None:
        """根据 ID 获取记录"""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, object] | None = None
    ) -> list[ModelType]:
        """获取记录列表"""
        stmt = select(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)  # type: ignore[arg-type]


        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def count(self, filters: dict[str, object] | None = None) -> int:
        """获取记录总数"""
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)  # type: ignore[arg-type]
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def create(self, obj_in: dict[str, object]) -> ModelType:
        """创建新记录"""
        db_obj = self.model(**obj_in)  # type: ignore[arg-type]
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict[str, object]) -> ModelType:
        """更新记录"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)  # type: ignore[arg-type]

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> ModelType | None:
        """删除记录"""
        db_obj = await self.get(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
        return db_obj
