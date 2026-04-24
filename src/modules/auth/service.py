from datetime import timedelta
from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.core.database import get_db
from src.core.exception import (APIException, AuthenticationException,
                                PermissionException)
from src.models.auth import Account, Role
from src.modules.auth.schemas import LoginForm, RegisterForm
from src.modules.auth.utils import (create_access_token, create_refresh_token,
                                    get_password_hash, verify_access_token,
                                    verify_password)

# ==============================
# 认证模块业务逻辑层：用户注册、登录认证
# 处理账户注册校验、密码加密、登录验证、Token生成
# ==============================


async def register_new_account(form: RegisterForm, db: AsyncSession) -> Account:
    """
    用户注册新账户

    业务逻辑：
        1. 校验邮箱是否已被注册
        2. 对用户密码进行哈希加密
        3. 创建新账户并保存到数据库

    Args:
        form: 注册表单数据，包含用户名、邮箱、密码
        db: 异步数据库会话

    Returns:
        Account: 注册成功的账户模型对象

    Raises:
        APIException: 邮箱已注册时抛出
    """
    # 查询数据库中是否已存在当前邮箱
    result = await db.execute(select(Account).where(Account.email == form.email))
    existing = result.scalar_one_or_none()

    # 邮箱已注册，抛出异常
    if existing:
        raise APIException(msg="邮箱已注册")

    # 密码加密处理
    hashed_pwd = get_password_hash(form.password)

    # 创建新账户对象
    account = Account(name=form.name, email=form.email, password=hashed_pwd)

    # 添加到数据库会话并提交事务
    db.add(account)
    await db.commit()

    return account


async def authenticate_account(form_data: LoginForm, db: AsyncSession):
    """
    用户登录认证

    业务逻辑：
        1. 根据邮箱查询账户是否存在
        2. 验证密码是否正确
        3. 生成JWT访问令牌
        4. 返回用户信息+令牌信息

    Args:
        form_data: 登录表单数据，包含邮箱、密码
        db: 异步数据库会话

    Returns:
        dict: 登录成功响应数据，包含用户信息、token、过期时间等

    Raises:
        APIException: 账户不存在或密码错误时抛出
    """
    # 根据邮箱查询账户
    stmt = select(Account).where(Account.email == form_data.email)
    result = await db.execute(stmt)
    account = result.scalars().first()

    # 账户不存在
    if not account:
        raise APIException(msg="账户不存在")

    # 密码校验失败
    if not verify_password(form_data.password, str(account.password)):
        raise APIException(msg="账号或密码错误")

    # 计算Token过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 生成JWT访问令牌，携带用户ID和邮箱作为载荷
    access_token = create_access_token(
        data={"id": account.id, "email": account.email},
        expires_delta=access_token_expires,
    )

    # 生成刷新令牌
    refresh_token = create_refresh_token(
        data={"id": account.id, "email": account.email}
    )

    # 构造登录成功返回数据
    return {
        "id": account.id,
        "name": account.name,
        "email": account.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict[str, str]:
    """
    使用刷新令牌获取新的访问令牌

    Args:
        refresh_token: 刷新令牌
        db: 异步数据库会话

    Returns:
        dict: 包含新的 access_token 和 refresh_token

    Raises:
        AuthenticationException: 刷新令牌无效或过期时抛出
    """
    # 验证刷新令牌
    payload = verify_access_token(refresh_token)
    if not payload:
        raise AuthenticationException(msg="刷新令牌已过期，请重新登录")

    # 检查令牌类型
    token_type = payload.get("type")
    if token_type != "refresh":
        raise AuthenticationException(msg="无效的刷新令牌")

    # 获取用户ID
    account_id = payload.get("id")
    if not account_id:
        raise AuthenticationException(msg="无效凭证")

    # 查询用户是否存在
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalars().first()
    if not account:
        raise AuthenticationException(msg="账户不存在")

    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"id": account.id, "email": account.email},
        expires_delta=access_token_expires,
    )

    # 生成新的刷新令牌（实现滚动刷新）
    new_refresh_token = create_refresh_token(
        data={"id": account.id, "email": account.email}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@lru_cache(maxsize=128)
async def get_current_account(
    request: Request, db: AsyncSession = Depends(get_db)
) -> Account:
    """
    获取当前登录用户（标准规范版）
    自动从请求头 Authorization: Bearer <token> 获取token并校验

    流程：
        1. 从请求头获取token
        2. 校验token是否有效
        3. 解析出用户ID
        4. 查询数据库返回用户
    """
    # 从请求头获取 token
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise AuthenticationException(msg="未提供身份凭证")

    # 拆分 Bearer 和 token（捕获具体异常，修复 E722）
    try:
        token_type, token = authorization.split()
        if token_type.lower() != "bearer":
            raise AuthenticationException(msg="凭证类型错误")
    except ValueError:
        raise AuthenticationException(msg="凭证格式错误")

    # 校验 token
    payload = verify_access_token(token)
    if not payload:
        raise AuthenticationException(msg="登录已过期，请重新登录")

    # 获取用户ID
    account_id = payload.get("id")
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
    return account


def _match_path_pattern(pattern: str, path: str) -> bool:
    """
    匹配路径模式

    Args:
        pattern: 路径模式
        path: 实际路径

    Returns:
        bool: 是否匹配
    """
    return pattern.strip("/") == path.strip("/")


def _match_method_pattern(menu_method: str, request_method: str) -> bool:
    """
    匹配请求方式

    Args:
        menu_method: 菜单配置的请求方式（GET/POST/PUT/DELETE/*）
        request_method: 实际请求方式

    Returns:
        bool: 是否匹配
    """
    if menu_method == "*":
        return True
    return menu_method.upper() == request_method.upper()


async def has_permission(
    account: Account, request_path: str, request_method: str
) -> bool:
    """
    检查用户是否有访问权限

    业务逻辑：
        1. 获取用户的所有角色
        2. 获取所有角色关联的菜单
        3. 检查请求路径是否匹配菜单的 api_url 模式
        4. 检查请求方式是否匹配菜单的 api_method

    Args:
        account: 账户对象
        request_path: 请求路径
        request_method: 请求方式

    Returns:
        bool: 是否有权限
    """
    # 遍历所有角色的菜单
    for role in account.roles:
        for menu in role.menus:
            if menu.api_url:
                # 检查路径匹配
                if _match_path_pattern(menu.api_url, request_path):
                    # 检查请求方式匹配
                    if _match_method_pattern(menu.api_method, request_method):
                        return True

    return False


async def check_permission(request: Request, db: AsyncSession = Depends(get_db)):
    """
    权限检查依赖

    业务逻辑：
        1. 获取当前登录用户
        2. 检查用户是否有权限访问请求路径和请求方式
        3. 如果没有权限，抛出 PermissionException 异常

    Args:
        request: 请求对象
        db: 异步数据库会话

    Returns:
        None

    Raises:
        PermissionException: 没有权限时抛出
    """
    # 获取当前登录用户
    account = await get_current_account(request, db)

    # 获取请求路径和请求方式
    request_path = request.url.path
    request_method = request.method

    # 检查权限
    permission_granted = await has_permission(account, request_path, request_method)

    # 如果没有权限，抛出异常
    if not permission_granted:
        raise PermissionException()
    # 有权限，继续处理请求
    return None
