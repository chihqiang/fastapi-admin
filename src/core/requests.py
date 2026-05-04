"""
FastAPI Request 辅助函数
"""

from fastapi import Request

from src.core.exception import AuthenticationException


def get_bearer_token(request: Request) -> str:
    """
    从 FastAPI Request 对象中提取 JWT token

    从请求头 Authorization: Bearer <token> 中提取 token。

    Args:
        request: FastAPI Request 对象

    Returns:
        str: JWT token 字符串

    Raises:
        AuthenticationException: 无法获取 token 时抛出
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise AuthenticationException(msg="未提供身份凭证")

    try:
        token_type, token = authorization.split()
        if token_type.lower() != "bearer":
            raise AuthenticationException(msg="凭证类型错误")
        return token
    except ValueError:
        raise AuthenticationException(msg="凭证格式错误")
