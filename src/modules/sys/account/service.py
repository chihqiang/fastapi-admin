"""
账号服务层

职责：
- 账号 CRUD 操作
- 业务逻辑处理和数据验证
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.exception import APIException
from src.models.auth import Account, Role
from src.modules.sys.account.schemas import (
    AccountCreate,
    AccountInfo,
    AccountListRequest,
    AccountListResponse,
    AccountUpdate,
)


class AccountService:
    """账号服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, request: AccountListRequest) -> AccountListResponse:
        """获取账号列表"""
        filters: dict[str, object] | None = {"id": request.id} if request.id else None
        total = await self._count(filters=filters)

        accounts = await self._list_with_roles(
            skip=request.offset, limit=request.size, account_id=request.id
        )

        account_list = [AccountInfo.model_validate(account) for account in accounts]

        return AccountListResponse(
            data=account_list,
            total=total,
            page=request.page,
            size=request.size,
        )

    async def get_detail(self, account_id: int) -> AccountInfo:
        """获取账号详情"""
        account = await self._get_with_roles(account_id)
        if not account:
            raise APIException(msg="账号不存在")

        return AccountInfo.model_validate(account)

    async def create(self, account_data: AccountCreate) -> AccountInfo:
        """创建账号"""
        if await self._get_by_email(account_data.email):
            raise APIException(msg="邮箱已存在")

        account = Account(
            name=account_data.name,
            email=account_data.email,
            status=account_data.status,
        )
        account.set_password(account_data.password)
        self.db.add(account)

        if account_data.roles:
            role_ids = [role.id for role in account_data.roles]
            roles = await self._get_roles_by_ids(role_ids)
            account.roles = roles

        await self.db.commit()
        await self.db.refresh(account)

        return await self.get_detail(account.id)

    async def update(self, account_id: int, account_data: AccountUpdate) -> AccountInfo:
        """更新账号"""
        account = await self._get_with_roles(account_id)
        if not account:
            raise APIException(msg="账号不存在")

        if account_data.email != account.email:
            if await self._get_by_email(account_data.email):
                raise APIException(msg="邮箱已存在")

        for field, value in account_data.model_dump(
            exclude={"roles", "password"}, exclude_unset=True
        ).items():
            setattr(account, field, value)

        if account_data.password:
            account.set_password(account_data.password)

        if account_data.roles is not None:
            role_ids = [role.id for role in account_data.roles]
            account.roles = await self._get_roles_by_ids(role_ids)

        await self.db.commit()
        await self.db.refresh(account)

        return await self.get_detail(account_id)

    async def delete(self, account_id: int, current_account: Account | None = None) -> None:
        """删除账号"""
        if current_account and account_id == current_account.id:
            raise APIException(msg="不能删除当前登录账户")

        if not await self._delete(account_id):
            raise APIException(msg="账号不存在")

    # ==================== 私有方法 ====================

    async def _get_by_email(self, email: str) -> Account | None:
        """根据邮箱获取账号"""
        stmt = select(Account).where(Account.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _get_with_roles(self, account_id: int) -> Account | None:
        """获取带角色的账号详情"""
        stmt = (
            select(Account)
            .options(joinedload(Account.roles))
            .where(Account.id == account_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def _list_with_roles(
        self, skip: int = 0, limit: int = 10, account_id: int | None = None
    ) -> list[Account]:
        """分页获取带角色的账号列表"""
        stmt = select(Account).options(selectinload(Account.roles))
        if account_id:
            stmt = stmt.where(Account.id == account_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def _count(self, filters: dict[str, object] | None = None) -> int:
        """获取记录总数"""
        from sqlalchemy import func, select

        stmt = select(func.count()).select_from(Account)
        if filters:
            for field, value in filters.items():
                if hasattr(Account, field):
                    stmt = stmt.where(getattr(Account, field) == value)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def _get_roles_by_ids(self, role_ids: list[int]) -> list[Role]:
        """根据ID列表获取角色"""
        stmt = select(Role).where(Role.id.in_(role_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _delete(self, account_id: int) -> bool:
        """删除账号"""
        stmt = select(Account).where(Account.id == account_id)
        result = await self.db.execute(stmt)
        account = result.scalars().first()
        if account:
            await self.db.delete(account)
            await self.db.commit()
            return True
        return False
