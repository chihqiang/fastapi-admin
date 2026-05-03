from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exception import APIException, AuthenticationException
from src.models.auth import Account
from src.modules.auth.schemas import (LoginForm, LoginOutSchema,
                                      RefreshTokenOutSchema, RegisterForm,
                                      RegisterOutSchema)

# ==============================
# 认证模块业务逻辑层：用户注册、登录认证
# 处理账户注册校验、密码加密、登录验证、Token生成
# ==============================


async def register_new_account(
    form: RegisterForm, db: AsyncSession
) -> RegisterOutSchema:
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
        RegisterOutSchema: 注册成功响应

    Raises:
        APIException: 邮箱已注册时抛出
    """
    # 查询数据库中是否已存在当前邮箱
    result = await db.execute(select(Account).where(Account.email == form.email))
    existing = result.scalar_one_or_none()

    # 邮箱已注册，抛出异常
    if existing:
        raise APIException(msg="邮箱已注册")

    # 创建新账户对象
    account = Account(name=form.name, email=form.email, password=form.password)
    account.set_password(form.password)

    # 添加到数据库会话并提交事务
    db.add(account)
    await db.commit()

    return RegisterOutSchema(
        id=account.id,
        name=account.name,
        email=account.email,
    )


async def authenticate_account(
    form_data: LoginForm, db: AsyncSession
) -> LoginOutSchema:
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
        LoginOutSchema: 登录成功响应

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
    if not account.verify_password(form_data.password):
        raise APIException(msg="账号或密码错误")

    # 生成JWT访问令牌和刷新令牌
    access_token = account.create_access_token()
    refresh_token = account.create_refresh_token()

    return LoginOutSchema(
        id=account.id,
        name=account.name,
        email=account.email,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


async def refresh_access_token(
    refresh_token: str, db: AsyncSession
) -> RefreshTokenOutSchema:
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
    payload = Account.verify_access_token(refresh_token)
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

    # 生成新的访问令牌和刷新令牌
    new_access_token = account.create_access_token()
    new_refresh_token = account.create_refresh_token()

    return RefreshTokenOutSchema(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
