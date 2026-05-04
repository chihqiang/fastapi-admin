"""
全局单例实例
"""

from src.core.config import settings
from src.utils.hashs import Token

# 全局 Token 处理器
token_instance = Token(
    secret_key=settings.SECRET_KEY,
    algorithm=settings.ALGORITHM,
    access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
)
