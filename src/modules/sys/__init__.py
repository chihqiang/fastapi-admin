"""
系统管理模块
"""

from src.modules.sys.account import router as account_router
from src.modules.sys.menu import router as menu_router
from src.modules.sys.role import router as role_router

__all__ = ["account_router", "role_router", "menu_router"]
