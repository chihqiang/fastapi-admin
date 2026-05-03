from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthPermission
from src.models.auth import Account
from src.modules.sys.account.schemas import (AccountCreate, AccountInfo,
                                             AccountListRequest,
                                             AccountListResponse,
                                             AccountUpdate)
from src.modules.sys.account.service import (create_account, delete_account,
                                             get_account_detail,
                                             get_account_list, update_account)
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/account", tags=["系统管理-账号管理"])


@router.get("/list", response_model=ApiResponse[AccountListResponse])
async def account_list(
    request: Annotated[AccountListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/account/list", api_method="GET"))
    ],
):
    """
    获取账号列表

    - **page**: 页码，默认 1
    - **size**: 每页数量，默认 10
    - **id**: 账号ID，用于精确搜索
    """
    result = await get_account_list(request, db)
    return success(data=result)


@router.get("/detail", response_model=ApiResponse[AccountInfo])
async def account_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/detail", api_method="GET")),
    ],
):
    """
    获取账号详情

    - **id**: 账号ID
    """
    result = await get_account_detail(id, db)
    return success(data=result)


@router.post("/create", response_model=ApiResponse[AccountInfo])
async def account_create(
    account_data: AccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/create", api_method="POST")),
    ],
):
    """
    创建账号

    - **name**: 用户名
    - **email**: 邮箱
    - **password**: 密码
    - **status**: 状态，默认 True
    - **roles**: 角色列表，每个元素为 {"id": 角色ID}
    """
    result = await create_account(account_data, db)
    return success(msg="创建成功", data=result)


@router.put("/update", response_model=ApiResponse[AccountInfo])
async def account_update(
    account_data: AccountUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/update", api_method="PUT")),
    ],
):
    """
    更新账号

    - **id**: 账号ID
    - **name**: 用户名
    - **email**: 邮箱
    - **password**: 密码（可选）
    - **status**: 状态
    - **roles**: 角色列表，每个元素为 {"id": 角色ID}
    """
    result = await update_account(account_data.id, account_data, db)
    return success(msg="更新成功", data=result)


@router.delete("/delete", response_model=ApiResponse[None])
async def account_delete(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/account/delete", api_method="DELETE")),
    ],
):
    """
    删除账号

    - **id**: 账号ID
    """
    await delete_account(id, db)
    return success(msg="删除成功")
