from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import APIException
from src.models.auth import Account
from src.modules.sys.account.repository import AccountRepository
from src.modules.sys.account.schemas import (AccountCreate, AccountInfo,
                                             AccountListRequest,
                                             AccountListResponse,
                                             AccountUpdate)


async def get_account_list(
    request: AccountListRequest, db: AsyncSession
) -> AccountListResponse:
    """获取账号列表"""
    repo = AccountRepository(db)

    # 获取总数
    filters: dict[str, object] | None = {"id": request.id} if request.id else None
    total = await repo.count(filters=filters)

    # 获取列表
    accounts = await repo.list_with_roles(
        skip=request.offset, limit=request.size, account_id=request.id
    )

    # 使用 model_validate 进行自动化模型转 Schema
    account_list = [AccountInfo.model_validate(account) for account in accounts]

    return AccountListResponse(
        data=account_list,
        total=total,
        page=request.page,
        size=request.size,
    )


async def get_account_detail(account_id: int, db: AsyncSession) -> AccountInfo:
    """获取账号详情"""
    repo = AccountRepository(db)
    account = await repo.get_with_roles(account_id)

    if not account:
        raise APIException(msg="账号不存在")

    return AccountInfo.model_validate(account)


async def create_account(account_data: AccountCreate, db: AsyncSession) -> AccountInfo:
    """创建账号"""
    repo = AccountRepository(db)

    # 检查邮箱
    if await repo.get_by_email(account_data.email):
        raise APIException(msg="邮箱已存在")

    # 创建账号（不立即 commit，保持在同一事务中）
    account = Account(
        name=account_data.name,
        email=account_data.email,
        status=account_data.status,
    )
    account.set_password(account_data.password)
    db.add(account)

    # 关联角色
    if account_data.roles:
        role_ids = [role.id for role in account_data.roles]
        roles = await repo.get_roles_by_ids(role_ids)
        account.roles = roles

    await db.commit()
    await db.refresh(account)

    return await get_account_detail(account.id, db)


async def update_account(
    account_id: int, account_data: AccountUpdate, db: AsyncSession
) -> AccountInfo:
    """更新账号"""
    repo = AccountRepository(db)
    account = await repo.get_with_roles(account_id)

    if not account:
        raise APIException(msg="账号不存在")

    # 检查邮箱
    if account_data.email != account.email:
        if await repo.get_by_email(account_data.email):
            raise APIException(msg="邮箱已存在")

    # 更新基础信息
    for field, value in account_data.model_dump(
        exclude={"roles", "password"}, exclude_unset=True
    ).items():
        setattr(account, field, value)

    # 更新密码
    if account_data.password:
        account.set_password(account_data.password)

    # 更新角色（在同一事务中）
    if account_data.roles is not None:
        role_ids = [role.id for role in account_data.roles]
        account.roles = await repo.get_roles_by_ids(role_ids)

    await db.commit()
    await db.refresh(account)

    return await get_account_detail(account_id, db)


async def delete_account(
    account_id: int, db: AsyncSession, current_account: Account
) -> None:
    """删除账号"""
    if account_id == current_account.id:
        raise APIException(msg="不能删除当前登录账户")

    repo = AccountRepository(db)
    if not await repo.delete(account_id):
        raise APIException(msg="账号不存在")
