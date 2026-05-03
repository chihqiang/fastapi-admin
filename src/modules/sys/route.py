from fastapi import APIRouter

from src.modules.sys.account import router as account_router
from src.modules.sys.menu import router as menu_router
from src.modules.sys.role import router as role_router

# 创建系统模块路由
router = APIRouter(prefix="/sys", tags=["系统管理"])

# 包含账号管理路由
router.include_router(account_router.router)

# 包含角色管理路由
router.include_router(role_router.router)

# 包含菜单管理路由
router.include_router(menu_router.router)
