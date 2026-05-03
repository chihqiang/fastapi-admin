from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthPermission
from src.models.auth import Account
from src.modules.sys.role.schemas import (RoleAssociateMenusRequest,
                                          RoleCreate, RoleInfo,
                                          RoleListRequest, RoleListResponse,
                                          RoleUpdate)
from src.modules.sys.role.service import (associate_role_menus, create_role,
                                          delete_role, get_all_roles,
                                          get_role_detail, get_role_list,
                                          update_role)
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/role", tags=["系统管理-角色管理"])


@router.get("/list", response_model=ApiResponse[RoleListResponse])
async def role_list(
    request: Annotated[RoleListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/list", api_method="GET"))
    ],
):
    """
    获取角色列表

    - **page**: 页码，默认 1
    - **size**: 每页数量，默认 10
    - **id**: 角色ID，用于精确搜索
    - **name**: 角色名称，用于模糊搜索
    """
    result = await get_role_list(request, db)
    return success(data=result)


@router.get("/detail", response_model=ApiResponse[RoleInfo])
async def role_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/detail", api_method="GET"))
    ],
):
    """
    获取角色详情

    - **id**: 角色ID
    """
    result = await get_role_detail(id, db)
    return success(data=result)


@router.post("/create", response_model=ApiResponse[RoleInfo])
async def role_create(
    role_data: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/create", api_method="POST"))
    ],
):
    """
    创建角色

    - **name**: 角色名称
    - **sort**: 排序，默认 0
    - **status**: 状态，默认 True
    - **remark**: 备注
    - **menus**: 菜单列表，每个元素为 {"id": 菜单ID}
    """
    result = await create_role(role_data, db)
    return success(msg="创建成功", data=result)


@router.put("/update", response_model=ApiResponse[RoleInfo])
async def role_update(
    role_data: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/update", api_method="PUT"))
    ],
):
    """
    更新角色

    - **id**: 角色ID
    - **name**: 角色名称
    - **sort**: 排序
    - **status**: 状态
    - **remark**: 备注
    - **menus**: 菜单列表，每个元素为 {"id": 菜单ID}
    """
    result = await update_role(role_data.id, role_data, db)
    return success(msg="更新成功", data=result)


@router.delete("/delete", response_model=ApiResponse[None])
async def role_delete(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/role/delete", api_method="DELETE")),
    ],
):
    """
    删除角色

    - **id**: 角色ID
    """
    await delete_role(id, db)
    return success(msg="删除成功")


@router.get("/all", response_model=ApiResponse[list[RoleInfo]])
async def role_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/all", api_method="GET"))
    ],
):
    """
    获取所有角色列表
    """
    result = await get_all_roles(db)
    return success(data=result)


@router.post("/associate-menus", response_model=ApiResponse[RoleInfo])
async def role_associate_menus(
    request: RoleAssociateMenusRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/role/associate-menus", api_method="POST")),
    ],
):
    """
    关联角色和菜单

    - **id**: 角色ID
    - **menu_ids**: 菜单ID列表
    """
    result = await associate_role_menus(request.id, request.menu_ids, db)
    return success(msg="关联成功", data=result)
