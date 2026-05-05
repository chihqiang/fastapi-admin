"""自动扫描并导入模块的工具"""

import importlib
import logging
import pkgutil
import sys
from pathlib import Path


class Loader:
    """
    装饰器：自动扫描并导入指定包或目录下的模块（支持子包），并记录导入结果日志。

    特性：
    - 支持包路径（如 "src.models"）和目录路径（如 "src/models"）
    - 可递归扫描子包
    - 支持函数执行前或后导入
    - 避免重复导入同一包
    - 支持同步函数（如需异步支持可扩展）
    - 支持排除指定模块
    - 导入失败会记录到日志，而不会抛出异常
    """

    _imported_packages: set[str] = set()  # 类级缓存，用于避免重复导入同一包

    def __init__(
        self,
        package: str | Path | None = None,
        recursive: bool = False,
        before: bool = False,
        exclude: list[str] | None = None,
    ):
        """
        初始化装饰器参数

        :param package: 要扫描的包名（如 "src.models"）或目录路径（如 "src/models"）
        :param recursive: 是否递归扫描子包，默认为 False
        :param before: 扫描时机，True 表示在函数执行前扫描，False 表示在函数执行后扫描
        :param exclude: 排除的模块名列表（不含后缀），默认为空列表
        """
        self.package = package
        self.recursive = recursive
        self.before = before
        self.exclude = exclude or []
        self.exclude_set: set[str] = {"__init__", *self.exclude}

    def __call__(self, func: callable):
        """
        装饰器入口，将扫描逻辑插入被装饰函数执行前或后

        :param func: 被装饰的函数
        :return: 包装后的函数
        """

        def wrapper(*args, **kwargs):
            # 前置扫描：函数执行前导入模块
            if self.before:
                self.scan_with_logging()

            # 执行原函数逻辑
            result = func(*args, **kwargs)

            # 后置扫描：函数执行后导入模块
            if not self.before:
                self.scan_with_logging()

            # 返回原函数返回值
            return result

        return wrapper

    def scan(self) -> None:
        """
        直接执行扫描和导入（不使用装饰器模式）
        """
        self.scan_with_logging()

    def _resolve_package_name(self) -> str | None:
        """
        解析包路径，将目录路径转为包名

        :return: 包名，如果解析失败返回 None
        """
        if not self.package:
            return None

        if isinstance(self.package, str) and "." in self.package:
            # 已经是包名格式
            return self.package
        else:
            # 处理目录路径
            try:
                dir_path = Path(self.package)
                if not dir_path.is_dir():
                    return None

                # 找到项目根目录（src 目录）
                project_root = dir_path
                while (
                    project_root.name != "src" and project_root.parent != project_root
                ):
                    project_root = project_root.parent

                # 把项目根目录加入 sys.path
                if project_root not in sys.path:
                    sys.path.insert(0, str(project_root))

                # 构造包名
                relative_path = dir_path.relative_to(project_root.parent)
                return str(relative_path).replace("/", ".").replace("\\", ".")
            except Exception:
                return None

    def scan_with_logging(self) -> None:
        """
        扫描包并导入模块，同时记录日志。

        日志规则：
        - 全部导入成功：输出 info 日志
        - 存在导入失败：输出 warning 日志
        """
        resolved_name = self._resolve_package_name()
        if not resolved_name:
            logging.warning(f"无法解析包路径: {self.package}")
            return

        success = self._import_package(resolved_name, self.recursive)

        if success:
            logging.info(f"成功导入 {resolved_name} 包下所有模块")
        else:
            logging.warning(f"{resolved_name} 包模块导入存在失败项")

    def _import_package(self, package_name: str, recursive: bool = False) -> bool:
        """
        扫描指定包及其模块并导入，返回导入结果。

        :param package_name: 要扫描的包名
        :param recursive: 是否递归扫描子包
        :return: True 表示全部导入成功，False 表示存在失败项
        """
        # 避免重复导入同一包
        if package_name in self._imported_packages:
            return True

        try:
            # 导入根包
            package = importlib.import_module(package_name)
            # 遍历包下所有模块和子包
            for _, module_name, is_package in pkgutil.iter_modules(package.__path__):
                # 检查是否在排除列表中
                if module_name in self.exclude_set:
                    continue
                module_path = f"{package_name}.{module_name}"
                try:
                    if is_package and recursive:
                        # 递归扫描子包
                        _ = self._import_package(module_path, recursive)
                    else:
                        # 导入普通模块
                        _ = importlib.import_module(module_path)
                except Exception:
                    # 捕获导入异常
                    return False
            # 标记包已扫描
            self._imported_packages.add(package_name)
            return True

        except Exception:
            return False
