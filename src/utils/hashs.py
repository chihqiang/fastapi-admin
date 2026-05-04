"""
密码和 Token 工具类

提供密码哈希和 JWT Token 管理的通用工具函数。

主要功能：
- 密码加密与验证（使用 bcrypt）
- JWT 访问令牌和刷新令牌的创建与验证

使用示例：
    # 密码处理
    hashed = pwd.set_password_hash("my_password")
    is_valid = pwd.verify_password(hashed, "my_password")

    # Token 处理
    token_handler = Token(secret_key="xxx", algorithm="HS256")
    access_token = token_handler.create_access_token(id=1, email="test@example.com")
    payload = token_handler.verify_token(access_token)
"""

from datetime import datetime, timedelta, timezone
from typing import TypedDict, cast

import bcrypt
from jose import JWTError, jwt


class TokenPayload(TypedDict):
    """JWT Token Payload 类型定义"""

    id: int
    email: str
    exp: datetime
    type: str


class pwd:
    """
    密码处理类

    提供密码哈希生成和验证功能，使用 bcrypt 算法。

    密码存储策略：
        1. 注册时：使用 set_password_hash() 生成哈希并存储
        2. 登录时：使用 verify_password() 验证用户输入的密码
    """

    @classmethod
    def set_password_hash(cls, password: str) -> str:
        """
        密码加密：生成密码哈希

        使用 bcrypt 算法对密码进行单向哈希加密。

        Args:
            password: 明文密码

        Returns:
            str: bcrypt 哈希后的密码字符串

        Example:
            hashed = pwd.set_password_hash("my_secure_password")
        """
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    @classmethod
    def verify_password(cls, hashed_password: str, plain_password: str) -> bool:
        """
        密码验证：对比明文密码与哈希密码

        使用 bcrypt.checkpw() 验证密码是否匹配。

        Args:
            hashed_password: 数据库中存储的哈希密码
            plain_password: 用户输入的明文密码

        Returns:
            bool: 密码匹配返回 True，否则返回 False
        """
        try:
            password_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(plain_password.encode("utf-8"), password_bytes)
        except (ValueError, AttributeError):
            return False


class Token:
    """
    JWT Token 处理类

    提供访问令牌和刷新令牌的创建与验证功能。

    令牌类型：
        - access: 访问令牌，用于 API 认证，短期有效
        - refresh: 刷新令牌，用于获取新的访问令牌，长期有效

    令牌 Payload 结构：
        - id: 用户 ID
        - email: 用户邮箱
        - exp: 过期时间
        - type: 令牌类型 ("access" 或 "refresh")
    """

    secret_key: str  # JWT 签名密钥
    algorithm: str  # JWT 算法（如 HS256）
    access_token_expire_minutes: int  # 访问令牌默认过期分钟数
    refresh_token_expire_days: int  # 刷新令牌默认过期天数
    access_token_expires_delta: timedelta | None  # 自定义访问令牌过期时间

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        access_token_expires_delta: timedelta | None = None,
    ):
        """
        初始化 Token 处理器

        Args:
            secret_key: JWT 签名密钥，用于加密令牌
            algorithm: JWT 算法，默认 HS256
            access_token_expire_minutes: 访问令牌过期时间（分钟），默认 30
            refresh_token_expire_days: 刷新令牌过期时间（天），默认 7
            access_token_expires_delta: 自定义访问令牌过期时间（优先级高于 access_token_expire_minutes）
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.access_token_expires_delta = access_token_expires_delta

    def create_access_token(self, id: int, email: str) -> str:
        """
        创建 JWT 访问令牌

        访问令牌用于 API 接口认证，建议设置较短的过期时间。

        Args:
            id: 用户唯一标识
            email: 用户邮箱地址

        Returns:
            str: 加密后的 JWT 访问令牌字符串

        Example:
            token = token_handler.create_access_token(id=1, email="user@example.com")
        """
        expire = datetime.now(timezone.utc) + (
            self.access_token_expires_delta
            or timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode = {
            "id": id,
            "email": email,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, id: int, email: str) -> str:
        """
        创建 JWT 刷新令牌

        刷新令牌用于在访问令牌过期后获取新的令牌，建议设置较长的过期时间。

        Args:
            id: 用户唯一标识
            email: 用户邮箱地址

        Returns:
            str: 加密后的 JWT 刷新令牌字符串

        Example:
            token = token_handler.create_refresh_token(id=1, email="user@example.com")
        """
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )
        to_encode = {
            "id": id,
            "email": email,
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> TokenPayload | None:
        """
        验证 JWT token 是否有效

        验证令牌的签名和过期时间，返回解码后的 payload。

        Args:
            token: JWT 令牌字符串

        Returns:
            TokenPayload | None: 解码成功返回 TokenPayload，失败返回 None

        Example:
            payload = token_handler.verify_token(access_token)
            if payload:
                user_id = payload.get("id")
                token_type = payload.get("type")
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return cast(TokenPayload, cast(object, payload))
        except JWTError:
            return None
