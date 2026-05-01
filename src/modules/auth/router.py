from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.schemas import (LoginForm, MenuInfo, RefreshTokenForm,
                                      RegisterForm, RoleInfo)
from src.modules.auth.service import (authenticate_account,
                                      get_current_account,
                                      refresh_access_token,
                                      register_new_account)
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/auth", tags=["认证模块"])


@router.post("/register")
async def register(
    form: RegisterForm, db: Annotated[AsyncSession, Depends(get_db)]
) -> ApiResponse[dict[str, Any]]:
    account = await register_new_account(form, db)
    return success(
        msg="注册成功",
        data={"id": account.id, "name": account.name, "email": account.email},
    )


@router.post("/login")
async def login(
    login_form: LoginForm, db: Annotated[AsyncSession, Depends(get_db)]
) -> ApiResponse[dict[str, Any]]:
    data = await authenticate_account(login_form, db)
    return success(
        msg="登录成功",
        data=data,
    )


@router.post("/refresh")
async def refresh_token(
    form: RefreshTokenForm, db: Annotated[AsyncSession, Depends(get_db)]
) -> ApiResponse[dict[str, Any]]:
    """使用刷新令牌获取新的访问令牌"""
    data = await refresh_access_token(form.refresh_token, db)
    return success(msg="刷新成功", data=data)


@router.get("/user/profile")
async def user_profile(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    account = await get_current_account(request, db)
    # 构建角色信息列表
    roles = [RoleInfo(id=role.id, name=role.name) for role in account.roles]

    # 收集所有菜单并去重
    menu_dict = {}
    for role in account.roles:
        for menu in role.menus:
            if menu.id not in menu_dict:
                menu_dict[menu.id] = menu

    # 构建菜单信息列表
    menus = [
        MenuInfo(
            id=menu.id,
            pid=menu.pid,
            menu_type=menu.menu_type,
            name=menu.name,
            path=menu.path,
            component=menu.component,
            icon=menu.icon,
            sort=menu.sort,
            api_url=menu.api_url,
            api_method=menu.api_method,
            visible=menu.visible,
            status=menu.status,
            remark=menu.remark,
        )
        for menu in menu_dict.values()
    ]

    return success(
        msg="获取个人信息成功",
        data={
            "id": account.id,
            "name": account.name,
            "email": account.email,
            "roles": roles,
            "menus": menus,
        },
    )
