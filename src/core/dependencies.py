import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.core.database import get_db
from src.core.exception import AuthenticationException, PermissionException
from src.core.instance import token_instance
from src.core.requests import get_bearer_token
from src.models.auth import Account, Role


async def get_current_account(
    request: Request, db: Annotated[AsyncSession, Depends(get_db)]
) -> Account:
    """
    获取当前登录用户（支持 FastAPI 依赖注入）

    自动从请求头 Authorization: Bearer <token> 获取 token 并校验
    无需在端点中显式传递 request 参数

    Returns:
        Account: 当前登录账户对象

    Raises:
        AuthenticationException: token 无效或已过期时抛出
    """
    # 从请求头获取 token
    token = get_bearer_token(request)

    # 校验 token
    payload = token_instance.verify_token(token)
    if not payload:
        raise AuthenticationException(msg="登录已过期，请重新登录")

    # 获取用户ID
    account_id = payload.id
    if not account_id:
        raise AuthenticationException(msg="无效凭证")

    # 查询用户，预加载角色和菜单数据
    result = await db.execute(
        select(Account)
        .options(joinedload(Account.roles).joinedload(Role.menus))
        .where(Account.id == account_id)
    )
    account = result.scalars().unique().one_or_none()
    if not account:
        raise AuthenticationException(msg="账户不存在")
    request.state.account_id = account.id
    request.state.account_name = account.name
    return account


class AuthPermission:
    """
    基于菜单 API 路径和方法的权限验证

    根据用户角色关联的菜单，检查请求的 API 路径和方法是否有权限访问
    """

    def __init__(
        self,
        api_url: str | None = None,
        api_method: str = "*",
    ) -> None:
        """
        初始化权限验证

        参数:
        - api_url: API 路径，用于匹配菜单的 api_url 字段
        - api_method: API 请求方法，默认 "*" 表示任意方法
        """
        # 自动补充 API 前缀
        if api_url and not api_url.startswith(settings.API_V1_PREFIX):
            api_url = settings.API_V1_PREFIX + api_url
        self.api_url: str | None = api_url
        self.api_method: str = api_method.upper()

    @staticmethod
    @lru_cache(maxsize=128)
    def get_user_permissions(account: Account) -> set[tuple[str, str]]:
        """
        获取用户菜单权限集合（带缓存）

        参数:
        - account: 账户对象

        返回:
        - set[tuple[str, str]]: 用户权限集合，每项为 (api_url, api_method)
        """
        return {
            (menu.api_url, menu.api_method)
            for role in account.roles
            for menu in role.menus
            if menu.api_url and menu.status is True
        }

    async def __call__(
        self, account: Annotated[Account, Depends(get_current_account)]
    ) -> Account:
        """
        调用权限验证

        参数:
        - account (Account): 当前登录账户对象。

        返回:
        - Account: 账户对象。

        Raises:
        - PermissionException: 无权限时抛出
        """
        # 无需验证权限（未设置 api_url）
        if not self.api_url:
            return account

        # 超级管理员权限标识
        if self.api_url == "*" or self.api_url == "*:*":
            return account

        # 检查用户是否有角色
        if not account.roles:
            raise PermissionException(msg="无权限操作")

        # 获取用户菜单集合（使用缓存）
        user_menus = self.get_user_permissions(account)

        # 权限验证 - 检查路径和方法是否匹配
        has_permission = any(
            (url == self.api_url and (method == self.api_method or method == "*"))
            for url, method in user_menus
        )

        if not has_permission:
            logging.error(f"用户缺少权限: {self.api_url} {self.api_method}")
            raise PermissionException(msg="无权限操作")

        return account
