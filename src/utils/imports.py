"""自动扫描并导入模块的工具"""

from importlib import import_module
from pathlib import Path


def import_modules(
    path: str | Path | None = None,
    exclude: list[str] | None = None,
) -> None:
    """
    扫描指定目录或包下的所有 Python 模块并导入。

    Args:
        path: 目录路径或包路径，如 "src/models" 或 "src.models"
        exclude: 需要排除的模块名列表
    """
    exclude = exclude or []
    exclude_set = {*exclude, "__init__"}

    if path is None:
        return

    # 如果是包路径字符串，转为目录路径
    if isinstance(path, str) and "." in path:
        module = import_module(path)
        if hasattr(module, "__path__"):
            path = Path(module.__path__[0])
        else:
            return
    else:
        path = Path(path)

    if not path.exists():
        return

    # 扫描目录
    for py_file in path.glob("*.py"):
        if py_file.stem in exclude_set:
            continue

        # 构建完整的模块路径
        parent = path.parent
        parent_name = parent.name
        if parent_name and parent_name != "src":
            # 构建相对于 src 的模块路径
            rel_path = py_file.relative_to(parent)
            module_name = (
                str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
            )
        else:
            # 直接在 src 下的模块
            module_name = py_file.stem

        try:
            _ = import_module(module_name)
        except ImportError:
            pass


def get_models_metadata():
    """返回已加载的 Base.metadata（确保所有模型已注册）"""
    from src.core.database import Base

    # 导入 src/models 下的所有模型
    import_modules("src.models")

    return Base.metadata
