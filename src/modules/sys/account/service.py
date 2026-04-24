from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import APIException
from src.modules.auth.utils import get_password_hash
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
    filters = {"id": request.id} if request.id else None
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

    # 准备数据
    account_dict = account_data.model_dump(exclude={"roles"})
    account_dict["password"] = get_password_hash(account_data.password)

    # 创建基础账号
    account = await repo.create(account_dict)

    # 关联角色
    if account_data.roles:
        role_ids = [role.id for role in account_data.roles]
        # 重新获取账号以预加载 roles 关系，避免懒加载问题
        account = await repo.get_with_roles(account.id)
        account.roles = await repo.get_roles_by_ids(role_ids)
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
    update_data = account_data.model_dump(
        exclude={"roles", "password"}, exclude_unset=True
    )
    if account_data.password:
        update_data["password"] = get_password_hash(account_data.password)

    await repo.update(account, update_data)

    # 更新角色
    if account_data.roles is not None:
        role_ids = [role.id for role in account_data.roles]
        # 重新获取以预加载 roles 关系，避免懒加载问题
        account = await repo.get_with_roles(account_id)
        account.roles = await repo.get_roles_by_ids(role_ids)
        await db.commit()
        await db.refresh(account)

    return await get_account_detail(account_id, db)


async def delete_account(account_id: int, db: AsyncSession, current_account) -> None:
    """删除账号"""
    if account_id == current_account.id:
        raise APIException(msg="不能删除当前登录账户")

    repo = AccountRepository(db)
    if not await repo.delete(account_id):
        raise APIException(msg="账号不存在")
