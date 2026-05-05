from .auth import Account, Menu, Role
from .sys_log import SysLog

__all__ = ["Account", "Menu", "Role", "SysLog"]


def get_models_metadata():
    """返回已加载的 Base.metadata（确保所有模型已注册）"""
    from src.core.database import Base
    from src.utils.imports import Loader

    # 导入 src/models 下的所有模型
    loader = Loader("src.models")
    loader.scan()

    return Base.metadata
