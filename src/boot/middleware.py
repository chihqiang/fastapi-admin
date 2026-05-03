"""
中间件注册模块

注册 CORS 和 GZip 中间件
"""

import logging

from fastapi import FastAPI

from src.core.middlewares import CustomCORSMiddleware, CustomGZipMiddleware


def register_middlewares(app: FastAPI) -> None:
    """注册全局中间件"""
    logging.info("🔗 注册中间件...")

    app.add_middleware(CustomGZipMiddleware)
    logging.debug("  ✅ GZip压缩中间件")

    app.add_middleware(CustomCORSMiddleware)
    logging.debug("  ✅ CORS跨域中间件")
