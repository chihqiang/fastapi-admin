"""
中间件注册模块

注册 CORS 和 GZip 中间件
"""

from fastapi import FastAPI

from src.core.middlewares import CustomCORSMiddleware, CustomGZipMiddleware


def register_middlewares(app: FastAPI) -> None:
    """注册全局中间件"""
    app.add_middleware(CustomGZipMiddleware)
    app.add_middleware(CustomCORSMiddleware)
