"""
路由注册模块

注册所有 API 路由模块
"""

from fastapi import FastAPI

from src.core.config import settings
from src.modules.auth import router as auth_router
from src.modules.sys import route as sys_router


def register_routers(app: FastAPI) -> None:
    """注册所有路由"""
    prefix = settings.API_V1_PREFIX
    app.include_router(auth_router.router, prefix=prefix, tags=["auth"])
    app.include_router(sys_router.router, prefix=prefix, tags=["system"])
