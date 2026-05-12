"""
模型加载器
用于 Alembic 迁移时自动扫描并加载所有模型
"""

from src.core.config import settings
from src.utils.modules import Loader


def models_metadata():
    """自动扫描并加载 src/models 下所有模型文件，返回 SQLAlchemy Base.metadata"""
    # 1. 先导入 Base，确保元数据对象已初始化
    from src.core.database import Base

    # 2. 使用 Loader 自动扫描并导入所有模型（递归加载所有子目录）
    Loader(
        package=settings.ROOT_PATH.joinpath("src", "models"),
        recursive=False,
        before=True,
    ).scan()
    # 3. 返回已注册所有模型的元数据
    return Base.metadata
