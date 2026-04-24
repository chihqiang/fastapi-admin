from datetime import datetime, timedelta
from typing import Union

import bcrypt
from jose import JWTError, jwt

from src.core.config import settings


# 密码加密：将明文密码转换为哈希密码（与Go代码保持一致）
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


# 密码验证：对比明文密码与数据库哈希密码是否一致
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
    except ValueError:
        # 如果bcrypt验证失败（可能是旧格式的哈希），返回False
        return False


# 创建JWT访问令牌
def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    # 复制原始数据，避免修改传入的字典
    to_encode = data.copy()

    # 如果传入了过期时间，则使用自定义时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    # 未传入则使用默认过期时间：15分钟
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # 将过期时间加入载荷，并标记为 access token
    to_encode.update({"exp": expire, "type": "access"})

    # 使用配置中的密钥和算法生成JWT令牌
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    # 返回最终生成的Token字符串
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建JWT刷新令牌

    刷新令牌用于在访问令牌过期后获取新的访问令牌，有效期更长。
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # 标记为 refresh token
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str):
    """
    验证 JWT token 是否有效
    返回解析后的载荷，验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
