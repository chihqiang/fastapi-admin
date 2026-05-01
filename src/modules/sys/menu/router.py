from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.sys.menu.schemas import (MenuCreate, MenuInfo,
                                          MenuListRequest, MenuListResponse,
                                          MenuUpdate)
from src.modules.sys.menu.service import (create_menu, delete_menu,
                                          get_all_menus, get_menu_detail,
                                          get_menu_list, update_menu)
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/menu", tags=["系统管理-菜单管理"])


@router.get("/list", response_model=ApiResponse[MenuListResponse])
async def menu_list(
    request: Annotated[MenuListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    获取菜单列表

    - **page**: 页码，默认 1
    - **size**: 每页数量，默认 10
    - **id**: 菜单ID，用于精确搜索
    - **name**: 菜单名称，用于模糊搜索
    - **status**: 状态筛选
    """
    result = await get_menu_list(request, db)
    return success(data=result)


@router.get("/all", response_model=ApiResponse[list[MenuInfo]])
async def menu_all(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    获取所有菜单列表（用于下拉选择）
    """
    result = await get_all_menus(db)
    return success(data=result)


@router.get("/detail", response_model=ApiResponse[MenuInfo])
async def menu_detail(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    获取菜单详情

    - **id**: 菜单ID
    """
    result = await get_menu_detail(id, db)
    return success(data=result)


@router.post("/create", response_model=ApiResponse[MenuInfo])
async def menu_create(menu_data: MenuCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    创建菜单

    - **name**: 菜单名称
    - **menu_type**: 菜单类型：1-目录 2-菜单 3-按钮
    - **path**: 菜单路径
    - **component**: 菜单组件
    - **icon**: 菜单图标
    - **sort**: 排序，默认 0
    - **api_url**: API 接口地址
    - **api_method**: API 接口方法
    - **visible**: 是否可见
    - **status**: 状态，默认 True
    - **pid**: 父菜单ID
    - **remark**: 备注
    """
    result = await create_menu(menu_data, db)
    return success(msg="创建成功", data=result)


@router.put("/update", response_model=ApiResponse[MenuInfo])
async def menu_update(menu_data: MenuUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    更新菜单

    - **id**: 菜单ID
    - **name**: 菜单名称
    - **menu_type**: 菜单类型：1-目录 2-菜单 3-按钮
    - **path**: 菜单路径
    - **component**: 菜单组件
    - **icon**: 菜单图标
    - **sort**: 排序
    - **api_url**: API 接口地址
    - **api_method**: API 接口方法
    - **visible**: 是否可见
    - **status**: 状态
    - **pid**: 父菜单ID
    - **remark**: 备注
    """
    result = await update_menu(menu_data.id, menu_data, db)
    return success(msg="更新成功", data=result)


@router.delete("/delete", response_model=ApiResponse[None])
async def menu_delete(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    删除菜单

    - **id**: 菜单ID
    """
    await delete_menu(id, db)
    return success(msg="删除成功")
