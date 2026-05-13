"""
路由注册模块

功能：
    自动扫描 src/modules 目录下的所有模块
    发现包含 router 对象的模块（支持 router.py 或 route.py）
    自动注册到 FastAPI 应用

使用方式：
    只需在 src/modules 下创建模块目录，并在其中定义 router 对象即可
    无需手动导入、无需修改任何配置

示例：
    src/modules/auth/router.py    -> 自动注册
    src/modules/sys/route.py     -> 自动注册
"""

import importlib
import logging
from pathlib import Path

from fastapi import APIRouter, FastAPI

from src.core.config import settings
from src.utils.modules import Loader

# ==================== 统一配置 ====================
MODULES_PACKAGE = "src.modules"
ROUTER_FILENAMES = ("router", "route")


# ==================== 路由注册 ====================
@Loader(package=MODULES_PACKAGE, recursive=True, before=True)
def register_routers(app: FastAPI) -> None:
    """
    自动发现并注册所有路由
    扫描 src/modules 目录下的每个子模块
    从 router.py 或 route.py 中获取 router 并注册到应用
    """
    prefix = settings.API_V1_PREFIX
    modules_path = settings.ROOT_PATH / Path(*MODULES_PACKAGE.split("."))
    registered_modules: list[str] = []
    for path in modules_path.iterdir():
        if not path.is_dir() or path.name.startswith("_"):
            continue
        router = _get_router(path.name)
        if isinstance(router, APIRouter):
            app.include_router(router, prefix=prefix)
            registered_modules.append(path.name)
    logging.info(f"成功注册路由模块: {registered_modules}")

def _get_router(module_name: str) -> APIRouter | None:
    """
    从模块中获取 router 对象
    支持：router.py / route.py
    """
    for filename in ROUTER_FILENAMES:
        try:
            # 直接用包名导入，不需要路径！
            router_module = importlib.import_module(
                f"{MODULES_PACKAGE}.{module_name}.{filename}"
            )
            router = getattr(router_module, "router", None)
            if isinstance(router, APIRouter):
                return router
        except Exception:
            continue

    return None
