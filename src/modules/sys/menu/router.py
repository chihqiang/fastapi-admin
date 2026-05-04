"""
菜单管理模块路由

职责：
- 菜单 CRUD 操作
- 菜单树结构管理
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthPermission
from src.models.auth import Account
from src.modules.sys.menu.schemas import (
    MenuCreate,
    MenuInfo,
    MenuListRequest,
    MenuListResponse,
    MenuUpdate,
)
from src.modules.sys.menu.service import MenuService
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/menu", tags=["系统管理-菜单管理"])


@router.get(
    "/list",
    summary="获取菜单列表",
    description="分页查询菜单列表，支持按ID、名称精确搜索和状态筛选",
    response_model=ApiResponse[MenuListResponse],
)
async def menu_list(
    request: Annotated[MenuListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/menu/list", api_method="GET"))
    ],
):
    """获取菜单列表"""
    service = MenuService(db)
    result = await service.get_list(request)
    return success(data=result)


@router.get(
    "/all",
    summary="获取所有菜单",
    description="获取所有菜单列表，不分页，用于下拉选择和树形展示",
    response_model=ApiResponse[list[MenuInfo]],
)
async def menu_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/menu/all", api_method="GET"))
    ],
):
    """获取所有菜单列表"""
    service = MenuService(db)
    result = await service.get_all()
    return success(data=result)


@router.get(
    "/detail",
    summary="获取菜单详情",
    description="根据菜单ID获取菜单详细信息",
    response_model=ApiResponse[MenuInfo],
)
async def menu_detail(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/menu/detail", api_method="GET"))
    ],
):
    """获取菜单详情"""
    service = MenuService(db)
    result = await service.get_detail(id)
    return success(data=result)


@router.post(
    "/create",
    summary="创建菜单",
    description="创建新菜单，支持目录、菜单、按钮三种类型",
    response_model=ApiResponse[MenuInfo],
)
async def menu_create(
    menu_data: MenuCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/menu/create", api_method="POST"))
    ],
):
    """创建菜单"""
    service = MenuService(db)
    result = await service.create(menu_data)
    return success(msg="创建成功", data=result)


@router.put(
    "/update",
    summary="更新菜单",
    description="更新菜单信息，支持修改菜单类型、路径、组件等属性",
    response_model=ApiResponse[MenuInfo],
)
async def menu_update(
    menu_data: MenuUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/menu/update", api_method="PUT"))
    ],
):
    """更新菜单"""
    service = MenuService(db)
    result = await service.update(menu_data.id, menu_data)
    return success(msg="更新成功", data=result)


@router.delete(
    "/delete",
    summary="删除菜单",
    description="根据菜单ID删除菜单",
    response_model=ApiResponse[None],
)
async def menu_delete(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account,
        Depends(AuthPermission(api_url="/sys/menu/delete", api_method="DELETE")),
    ],
):
    """删除菜单"""
    service = MenuService(db)
    await service.delete(id)
    return success(msg="删除成功")
