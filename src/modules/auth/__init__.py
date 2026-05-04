"""
认证模块
"""

from src.modules.auth.router import router
from src.modules.auth.service import AuthService

__all__ = ["router", "AuthService"]
