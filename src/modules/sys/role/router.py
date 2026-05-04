"""
角色管理模块路由

职责：
- 角色 CRUD 操作
- 角色菜单关联管理
"""

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
from src.modules.sys.role.service import RoleService
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/role", tags=["系统管理-角色管理"])


@router.get(
    "/list",
    summary="获取角色列表",
    description="分页查询角色列表，支持按ID精确搜索和名称模糊搜索",
    response_model=ApiResponse[RoleListResponse],
)
async def role_list(
    request: Annotated[RoleListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/list", api_method="GET"))
    ],
):
    """获取角色列表"""
    service = RoleService(db)
    result = await service.get_list(request)
    return success(data=result)


@router.get(
    "/detail",
    summary="获取角色详情",
    description="根据角色ID获取角色详细信息",
    response_model=ApiResponse[RoleInfo],
)
async def role_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/detail", api_method="GET"))
    ],
):
    """获取角色详情"""
    service = RoleService(db)
    result = await service.get_detail(id)
    return success(data=result)


@router.post(
    "/create",
    summary="创建角色",
    description="创建新角色，可关联菜单权限",
    response_model=ApiResponse[RoleInfo],
)
async def role_create(
    role_data: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/create", api_method="POST"))
    ],
):
    """创建角色"""
    service = RoleService(db)
    result = await service.create(role_data)
    return success(msg="创建成功", data=result)


@router.put(
    "/update",
    summary="更新角色",
    description="更新角色信息，可修改关联的菜单权限",
    response_model=ApiResponse[RoleInfo],
)
async def role_update(
    role_data: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/update", api_method="PUT"))
    ],
):
    """更新角色"""
    service = RoleService(db)
    result = await service.update(role_data.id, role_data)
    return success(msg="更新成功", data=result)


@router.delete(
    "/delete",
    summary="删除角色",
    description="根据角色ID删除角色",
    response_model=ApiResponse[None],
)
async def role_delete(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/role/delete", api_method="DELETE")),
    ],
):
    """删除角色"""
    service = RoleService(db)
    await service.delete(id)
    return success(msg="删除成功")


@router.get(
    "/all",
    summary="获取所有角色",
    description="获取所有角色列表，不分页，用于下拉选择",
    response_model=ApiResponse[list[RoleInfo]],
)
async def role_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/role/all", api_method="GET"))
    ],
):
    """获取所有角色列表"""
    service = RoleService(db)
    result = await service.get_all()
    return success(data=result)


@router.post(
    "/associate-menus",
    summary="关联角色菜单",
    description="为角色分配或更新菜单权限",
    response_model=ApiResponse[RoleInfo],
)
async def role_associate_menus(
    request: RoleAssociateMenusRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/role/associate-menus", api_method="POST")),
    ],
):
    """关联角色和菜单"""
    service = RoleService(db)
    result = await service.associate_menus(request.id, request.menu_ids)
    return success(msg="关联成功", data=result)
