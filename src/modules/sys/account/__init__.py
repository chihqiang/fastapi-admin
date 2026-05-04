"""
账号管理模块
"""

from src.modules.sys.account.router import router
from src.modules.sys.account.service import AccountService

__all__ = ["router", "AccountService"]
