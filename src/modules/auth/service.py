"""
认证服务层

职责：
- 用户注册、登录、Token 管理
- 业务逻辑处理和数据验证
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.core.exception import APIException, AuthenticationException
from src.core.instance import token_instance
from src.models.auth import Account, Role
from src.modules.auth.schemas import (LoginForm, LoginOutSchema, MenuInfo,
                                      ProfileOutSchema, RefreshTokenOutSchema,
                                      RegisterForm, RegisterOutSchema,
                                      RoleInfo)
from src.utils.hashs import TokenType, pwd


class AuthService:
    """认证服务类"""

    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, form: RegisterForm) -> RegisterOutSchema:
        """用户注册"""
        existing = await self._get_by_email(form.email)
        if existing:
            raise APIException(msg="邮箱已注册")

        account = Account(
            name=form.name,
            email=form.email,
            password=pwd.set_password_hash(form.password),
        )

        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        return RegisterOutSchema(
            id=account.id,
            name=account.name,
            email=account.email,
        )

    async def login(self, form_data: LoginForm) -> LoginOutSchema:
        """用户登录认证"""
        account = await self._get_by_email(form_data.email)
        if not account:
            raise APIException(msg="账户不存在")

        if not pwd.verify_password(account.password, form_data.password):
            raise APIException(msg="账号或密码错误")

        access_token = token_instance.create_access_token(
            id=account.id, email=account.email
        )
        refresh_token = token_instance.create_refresh_token(
            id=account.id, email=account.email
        )

        return LoginOutSchema(
            id=account.id,
            name=account.name,
            email=account.email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    async def refresh_token(self, refresh_token: str) -> RefreshTokenOutSchema:
        """使用刷新令牌获取新的访问令牌"""
        payload = token_instance.verify_token(refresh_token)
        if not payload:
            raise AuthenticationException(msg="刷新令牌已过期，请重新登录")

        if payload.type != TokenType.REFRESH:
            raise AuthenticationException(msg="无效的刷新令牌")

        account_id = payload.id
        if not account_id:
            raise AuthenticationException(msg="无效凭证")

        account = await self._get_by_id(account_id)
        if not account:
            raise AuthenticationException(msg="账户不存在")

        new_access_token = token_instance.create_access_token(
            id=account.id, email=account.email
        )
        new_refresh_token = token_instance.create_refresh_token(
            id=account.id, email=account.email
        )

        return RefreshTokenOutSchema(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    async def get_profile(self, account: Account) -> ProfileOutSchema:
        """获取当前用户资料和权限菜单"""
        stmt = (
            select(Account)
            .options(joinedload(Account.roles).joinedload(Role.menus))
            .where(Account.id == account.id)
        )
        result = await self.db.execute(stmt)
        account = result.scalars().unique().one()

        roles = [RoleInfo.model_validate(role) for role in account.roles]

        menu_dict: dict[int, MenuInfo] = {}
        for role in account.roles:
            for menu in role.menus:
                if menu.id not in menu_dict:
                    menu_dict[menu.id] = MenuInfo.model_validate(menu)

        return ProfileOutSchema(
            id=account.id,
            name=account.name,
            email=account.email,
            roles=roles,
            menus=list(menu_dict.values()),
        )

    # ==================== 私有方法 ====================

    async def _get_by_email(self, email: str) -> Account | None:
        """根据邮箱获取账号"""
        stmt = select(Account).where(Account.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _get_by_id(self, account_id: int) -> Account | None:
        """根据ID获取账号"""
        stmt = select(Account).where(Account.id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
