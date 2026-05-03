"""
路由注册模块

注册所有 API 路由模块
"""

import logging

from fastapi import FastAPI

from src.core.config import settings
from src.modules.auth import router as auth_router
from src.modules.sys import route as sys_router


def register_routers(app: FastAPI) -> None:
    """注册所有路由"""
    prefix = settings.API_V1_STR
    logging.info(f"🛣️  注册路由 (prefix: {prefix})...")

    app.include_router(auth_router.router, prefix=prefix, tags=["auth"])
    logging.debug("  ✅ auth 路由注册完成")

    app.include_router(sys_router.router, prefix=prefix, tags=["system"])
    logging.debug("  ✅ system 路由注册完成")
