from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_account
from src.models.auth import Account
from src.modules.auth.schemas import (LoginForm, LoginOutSchema, MenuInfo,
                                      ProfileOutSchema, RefreshTokenForm,
                                      RefreshTokenOutSchema, RegisterForm,
                                      RegisterOutSchema, RoleInfo)
from src.modules.auth.service import (authenticate_account,
                                      refresh_access_token,
                                      register_new_account)
from src.schemas.response import ApiResponse, success

router = APIRouter(prefix="/auth", tags=["认证模块"])


@router.post(
    "/register",
    summary="用户注册",
    description="用户注册接口，传入用户名、邮箱、密码进行注册",
    response_model=ApiResponse[RegisterOutSchema],
)
async def register(
    form: RegisterForm, db: Annotated[AsyncSession, Depends(get_db)]
) -> ApiResponse[RegisterOutSchema]:
    data = await register_new_account(form, db)
    return success(msg="注册成功", data=data)


@router.post(
    "/login",
    summary="用户登录",
    description="用户登录接口，传入邮箱、密码进行登录，返回访问令牌和刷新令牌",
    response_model=ApiResponse[LoginOutSchema],
)
async def login(
    login_form: LoginForm, db: Annotated[AsyncSession, Depends(get_db)]
) -> ApiResponse[LoginOutSchema]:
    data = await authenticate_account(login_form, db)
    return success(msg="登录成功", data=data)


@router.post(
    "/refresh",
    summary="刷新令牌",
    description="使用刷新令牌获取新的访问令牌",
    response_model=ApiResponse[RefreshTokenOutSchema],
)
async def refresh_token(
    form: RefreshTokenForm, db: Annotated[AsyncSession, Depends(get_db)]
) -> ApiResponse[RefreshTokenOutSchema]:
    data = await refresh_access_token(form.refresh_token, db)
    return success(msg="刷新成功", data=data)


@router.get(
    "/user/profile",
    summary="获取用户资料",
    description="获取当前登录用户的信息，包括角色和菜单权限",
    response_model=ApiResponse[ProfileOutSchema],
)
async def user_profile(
    current_account: Annotated[Account, Depends(get_current_account)],
) -> ApiResponse[ProfileOutSchema]:
    account = current_account

    # 构建角色信息列表
    roles = [RoleInfo.model_validate(role) for role in account.roles]

    # 收集所有菜单并去重
    menu_dict: dict[int, MenuInfo] = {}
    for role in account.roles:
        for menu in role.menus:
            if menu.id not in menu_dict:
                menu_dict[menu.id] = MenuInfo.model_validate(menu)

    return success(
        msg="获取个人信息成功",
        data=ProfileOutSchema(
            id=account.id,
            name=account.name,
            email=account.email,
            roles=roles,
            menus=list(menu_dict.values()),
        ),
    )
