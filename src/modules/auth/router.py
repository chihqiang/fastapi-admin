"""
认证模块路由

职责：
- 用户注册、登录、Token 管理
- 获取用户资料和权限菜单
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_account
from src.models.auth import Account
from src.modules.auth.schemas import (LoginForm, LoginOutSchema,
                                      ProfileOutSchema, RefreshTokenForm,
                                      RefreshTokenOutSchema, RegisterForm,
                                      RegisterOutSchema)
from src.modules.auth.service import AuthService
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
    """用户注册"""
    service = AuthService(db)
    data = await service.register(form)
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
    """用户登录"""
    service = AuthService(db)
    data = await service.login(login_form)
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
    """刷新令牌"""
    service = AuthService(db)
    data = await service.refresh_token(form.refresh_token)
    return success(msg="刷新成功", data=data)


@router.get(
    "/user/profile",
    summary="获取用户资料",
    description="获取当前登录用户的信息，包括角色和菜单权限",
    response_model=ApiResponse[ProfileOutSchema],
)
async def user_profile(
    current_account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[ProfileOutSchema]:
    """获取用户资料"""
    service = AuthService(db)
    data = await service.get_profile(current_account)
    return success(msg="获取个人信息成功", data=data)
