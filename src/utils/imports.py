"""自动扫描并导入模块的工具"""

import sys
from importlib import import_module
from pathlib import Path


def import_modules(
    path: str | Path | None = None,
    exclude: list[str] | None = None,
) -> None:
    """
    稳定版：扫描指定目录或包下的所有 Python 模块并自动导入
    专门用于导入 models / schemas / routes / api 等

    Args:
        path: 目录路径（如 src/models）或 包路径（如 src.models）
        exclude: 排除的文件名（不含后缀）
    """
    exclude = exclude or []
    exclude_set = {"__init__", *exclude}
    if not path:
        return
    # ======================
    # 1. 处理包路径 → 转为真实目录
    # ======================
    if isinstance(path, str) and "." in path:
        try:
            module = import_module(path)
            if not hasattr(module, "__path__"):
                return
            dir_path = Path(module.__path__[0])
        except ImportError:
            return
    else:
        dir_path = Path(path)

    if not dir_path.is_dir():
        return
    # ======================
    # 2. 把项目根目录加入 sys.path（关键修复）
    # ======================
    project_root = dir_path
    while project_root.name != "src" and project_root.parent != project_root:
        project_root = project_root.parent
    if project_root not in sys.path:
        sys.path.insert(0, str(project_root))
    # ======================
    # 3. 扫描所有 .py 文件
    # ======================
    for py_file in dir_path.glob("*.py"):
        module_name = py_file.stem
        if module_name in exclude_set:
            continue
        # ======================
        # 4. 正确构造模块导入路径（核心修复）
        # ======================
        relative_path = py_file.relative_to(project_root.parent)
        import_path = (
            str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        )
        # ======================
        # 5. 安全导入
        # ======================
        try:
            import_module(import_path)
        except ImportError:
            continue


def get_models_metadata():
    """返回已加载的 Base.metadata（确保所有模型已注册）"""
    from src.core.database import Base

    # 导入 src/models 下的所有模型
    import_modules("src.models")

    return Base.metadata
