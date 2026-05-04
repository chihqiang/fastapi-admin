"""
账号管理模块路由

职责：
- 账号 CRUD 操作
- 账号角色关联管理
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthPermission, get_current_account
from src.models.auth import Account
from src.modules.sys.account.schemas import (AccountCreate, AccountInfo,
                                             AccountListRequest,
                                             AccountListResponse,
                                             AccountUpdate)
from src.modules.sys.account.service import AccountService
from src.schemas.response import ResponseSchema, success

router = APIRouter(prefix="/account", tags=["系统管理-账号管理"])


@router.get("/list", response_model=ResponseSchema[AccountListResponse])
async def account_list(
    request: Annotated[AccountListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/account/list", api_method="GET"))
    ],
):
    """获取账号列表"""
    service = AccountService(db)
    result = await service.get_list(request)
    return success(data=result)


@router.get("/detail", response_model=ResponseSchema[AccountInfo])
async def account_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/detail", api_method="GET")),
    ],
):
    """获取账号详情"""
    service = AccountService(db)
    result = await service.get_detail(id)
    return success(data=result)


@router.post("/create", response_model=ResponseSchema[AccountInfo])
async def account_create(
    account_data: AccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/create", api_method="POST")),
    ],
):
    """创建账号"""
    service = AccountService(db)
    result = await service.create(account_data)
    return success(msg="创建成功", data=result)


@router.put("/update", response_model=ResponseSchema[AccountInfo])
async def account_update(
    account_data: AccountUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/update", api_method="PUT")),
    ],
):
    """更新账号"""
    service = AccountService(db)
    result = await service.update(account_data.id, account_data)
    return success(msg="更新成功", data=result)


@router.delete("/delete", response_model=ResponseSchema[None])
async def account_delete(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_account: Annotated[Account, Depends(get_current_account)] = None,
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/delete", api_method="DELETE")),
    ] = None,
):
    """删除账号"""
    service = AccountService(db)
    await service.delete(id, current_account)
    return success(msg="删除成功")
