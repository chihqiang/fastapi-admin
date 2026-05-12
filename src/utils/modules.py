"""
通用模块自动加载工具
功能：支持按包名/目录路径 自动扫描并导入模块、子包
适用场景：Alembic模型自动加载、路由自动注册、插件自动注册等
"""

import importlib
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Any, Callable


class Loader:
    """
    模块自动加载装饰器 / 工具类
    核心能力：
        1. 支持传入 包名字符串 或 目录Path路径
        2. 可选递归扫描子包、自动跳过内置文件
        3. 装饰器模式：支持函数执行前/后触发导入
        4. 全局缓存已导入包，避免重复导入
        5. 支持自定义排除模块，导入异常只打日志不抛错
        6. 自动处理sys.path，解决模块找不到问题
    """

    # 全局类属性：缓存已导入的包名，全局去重
    _imported_packages: set[str] = set()

    def __init__(
        self,
        package: str | Path | None = None,
        recursive: bool = True,
        before: bool = False,
        exclude: list[str] | None = None,
    ):
        """
        初始化加载器配置
        :param package: 目标包名(如 src.models) 或 目录路径(如 src/models)
        :param recursive: 是否递归扫描子包，默认开启
        :param before: True=函数执行前导入，False=函数执行后导入
        :param exclude: 自定义需要排除的模块名列表，无需带后缀
        """
        self.package = package
        self.recursive = recursive
        self.before = before
        self.exclude = exclude or []

        # 默认排除：内置初始化文件、缓存目录 + 自定义排除项
        self.exclude_set = {"__init__", "__pycache__", *self.exclude}

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        装饰器入口方法
        实现被装饰函数的前置/后置模块导入逻辑
        """

        def wrapper(*args, **kwargs) -> Any:
            # 前置触发：函数执行前扫描导入
            if self.before:
                self.scan_with_logging()

            # 执行原业务函数
            result = func(*args, **kwargs)

            # 后置触发：函数执行后扫描导入
            if not self.before:
                self.scan_with_logging()

            return result

        return wrapper

    def scan(self) -> None:
        """
        独立调用入口：不依赖装饰器，直接执行模块扫描导入
        外部可主动调用此方法加载模块
        """
        self.scan_with_logging()

    def _resolve_package_name(self) -> str | None:
        """
        私有方法：路径智能解析
        将 目录Path/字符串路径 统一解析为 Python 标准包名
        自动补全sys.path，解决跨目录模块导入失败
        :return: 解析后的标准包名，解析失败返回None
        """
        if not self.package:
            return None

        pkg_str = str(self.package).strip()

        # 已经是带.的标准包名，直接返回
        if "." in pkg_str:
            return pkg_str

        # 处理本地目录路径
        try:
            dir_path = Path(pkg_str).resolve()
            if not dir_path.is_dir():
                return None

            # 将目录父级加入模块搜索路径
            parent_path = str(dir_path.parent)
            if parent_path not in sys.path:
                sys.path.insert(0, parent_path)

            # 匹配sys.path，拼接为标准包名
            for sys_path in sys.path:
                try:
                    rel_path = dir_path.relative_to(Path(sys_path).resolve())
                    return ".".join(rel_path.parts)
                except ValueError:
                    continue
            return None
        except Exception:
            return None

    def scan_with_logging(self) -> None:
        """
        带日志的扫描入口
        解析包名 -> 执行导入 -> 输出成功/失败日志
        """
        package_name = self._resolve_package_name()
        if not package_name:
            logging.warning(f"[Loader] 无法解析目标路径：{self.package}")
            return

        # 执行模块批量导入
        all_success = self._import_package(package_name, self.recursive)
        if all_success:
            logging.info(f"[Loader] 模块导入完成：{package_name}")
        else:
            logging.warning(f"[Loader] 存在模块导入失败：{package_name}")

    def _import_package(self, package_name: str, recursive: bool) -> bool:
        """
        私有递归导入核心方法
        遍历包下所有模块/子包，逐个导入，异常隔离不中断整体流程
        :param package_name: 待导入标准包名
        :param recursive: 是否递归子包
        :return: True=全部成功，False=存在导入失败
        """
        # 已导入直接跳过，避免重复加载
        if package_name in self._imported_packages:
            return True

        try:
            # 导入当前根包
            package = importlib.import_module(package_name)
            self._imported_packages.add(package_name)
            all_success = True

            # 遍历包下所有模块、子包
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                # 跳过排除列表内的模块
                if module_name in self.exclude_set:
                    continue

                full_module_path = f"{package_name}.{module_name}"

                try:
                    if is_pkg and recursive:
                        # 子包：递归继续导入
                        sub_success = self._import_package(
                            full_module_path, recursive=True
                        )
                        if not sub_success:
                            all_success = False
                    else:
                        # 普通模块：直接导入
                        importlib.import_module(full_module_path)
                        logging.debug(f"[Loader] 已导入：{full_module_path}")

                except Exception as e:
                    logging.error(f"[Loader] 导入失败 {full_module_path}：{str(e)}")
                    all_success = False

            return all_success

        except Exception as e:
            logging.error(f"[Loader] 包初始化失败 {package_name}：{str(e)}")
            return False
