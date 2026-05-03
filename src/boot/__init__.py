"""
应用启动和初始化模块

负责创建 FastAPI 应用实例，注册各种组件
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.boot.exception import register_exception
from src.boot.middleware import register_middlewares
from src.boot.route import register_routers

__all__ = ["create_app"]
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logging.info("=" * 50)
    logging.info("🚀 应用启动中...")
    logging.info("=" * 50)

    yield

    # Shutdown logic
    logging.info("=" * 50)
    logging.info("👋 应用关闭中...")
    logging.info("=" * 50)


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    logging.info(f"📦 创建应用: {settings.PROJECT_NAME}")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        lifespan=lifespan,
    )
    # 注册组件
    register_exception(app)
    register_middlewares(app)
    register_routers(app)

    logging.info("✅ 所有组件注册完成")
    logging.info("=" * 50)

    return app
