from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from typing_extensions import override

from src.core.config import settings

if TYPE_CHECKING:
    pass


class LogLevel(Enum):
    """日志级别枚举"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """日志格式枚举"""

    JSON = "json"
    CONSOLE = "console"
    TEXT = "text"


class JSONFormatter(logging.Formatter):
    """自定义 JSON 日志格式化器，输出结构化日志"""

    include_extra: bool = True

    @override
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加进程和线程信息
        log_obj["process_id"] = record.process
        log_obj["thread_id"] = record.thread

        # 添加异常信息
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # 添加自定义额外字段（通过 extra 传递）
        extra: dict[str, Any] = record.__dict__.get("extra", {})
        if extra:
            log_obj["extra"] = extra

        return json.dumps(log_obj, ensure_ascii=False, default=str)


class ConsoleFormatter(logging.Formatter):
    """控制台美化格式化器"""

    COLORS: dict[str, str] = {
        "DEBUG": "\x1b[36m",  # 青色
        "INFO": "\x1b[32m",  # 绿色
        "WARNING": "\x1b[33m",  # 黄色
        "ERROR": "\x1b[31m",  # 红色
        "CRITICAL": "\x1b[35m",  # 紫色
        "RESET": "\x1b[0m",
    }

    def __init__(self, use_color: bool = True) -> None:
        super().__init__()
        self.use_color = use_color and sys.stdout.isatty()

    @override
    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        color = self.COLORS.get(level, "")
        reset = self.COLORS["RESET"] if self.use_color else ""

        # 时间
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 格式化日志
        if self.use_color:
            return (
                f"{color}[{timestamp}]{reset} "
                f"{color}[{level:<8}]{reset} "
                f"[{record.module}:{record.lineno}] "
                f"{record.getMessage()}"
            )
        return (
            f"[{timestamp}] "
            f"[{level:<8}] "
            f"[{record.module}:{record.lineno}] "
            f"{record.getMessage()}"
        )


class StructuredLogger:
    """
    结构化日志记录器

    支持：
    - 多种日志格式（JSON、控制台、文本）
    - 请求上下文跟踪
    - 自定义额外数据
    - 日志轮转
    """

    _instances: dict[str, StructuredLogger] = {}
    name: str
    logger: logging.Logger

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        log_format: LogFormat = LogFormat.CONSOLE,
        log_file: str | Path | None = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ) -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value, logging.INFO))
        self.logger.propagate = False

        # 清除现有处理器
        self.logger.handlers.clear()

        # 添加处理器
        handlers: list[logging.Handler] = []

        # 控制台处理器
        console_handler = self._create_console_handler(log_format)
        handlers.append(console_handler)

        # 文件处理器（可选）
        if log_file:
            file_handler = self._create_file_handler(log_file, max_bytes, backup_count)
            handlers.append(file_handler)

        for handler in handlers:
            self.logger.addHandler(handler)

    def _create_console_handler(self, log_format: LogFormat) -> logging.Handler:
        """创建控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        if log_format == LogFormat.JSON:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(ConsoleFormatter(use_color=True))

        handler.setLevel(logging.DEBUG)
        return handler

    def _create_file_handler(
        self,
        log_file: str | Path,
        max_bytes: int,
        backup_count: int,
    ) -> logging.Handler:
        """创建文件处理器（带轮转）"""
        from logging.handlers import RotatingFileHandler

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            filename=str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        handler.setFormatter(JSONFormatter())
        handler.setLevel(logging.DEBUG)
        return handler

    def _log(
        self,
        level: int,
        message: str,
        exc_info: BaseException | None = None,
        **kwargs: Any,
    ) -> None:
        """带额外数据的日志记录"""
        extra: dict[str, Any] = kwargs if kwargs else {}
        self.logger.log(level, message, exc_info=exc_info, extra=extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def error(
        self, message: str, exc_info: BaseException | None = None, **kwargs: Any
    ) -> None:
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)

    def critical(
        self, message: str, exc_info: BaseException | None = None, **kwargs: Any
    ) -> None:
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: LogLevel = LogLevel.INFO,
        log_format: LogFormat = LogFormat.CONSOLE,
        log_file: str | Path | None = None,
    ) -> StructuredLogger:
        """获取或创建日志记录器实例（单例）"""
        if name not in cls._instances:
            cls._instances[name] = cls(name, level, log_format, log_file)
        return cls._instances[name]


def setup_logging() -> None:
    """
    配置全局日志（配置从 src.core.config 读取）

    配置项:
        - LOG_LEVEL: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        - LOG_FORMAT: 日志格式 (json/console/text)
        - LOG_FILE: 日志文件路径，为 None 时不写入文件
    """
    level = LogLevel(settings.LOG_LEVEL)
    log_format = LogFormat(settings.LOG_FORMAT)
    log_file = settings.LOG_FILE

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.value, logging.INFO))

    # 移除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建处理器
    handlers: list[logging.Handler] = []

    # 控制台
    console_handler = logging.StreamHandler(sys.stdout)
    if log_format == LogFormat.JSON:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ConsoleFormatter(use_color=True))
    handlers.append(console_handler)

    # 文件（可选）
    if log_file:
        from logging.handlers import RotatingFileHandler

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(log_path),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(JSONFormatter())
        handlers.append(file_handler)

    # 添加处理器
    for handler in handlers:
        root_logger.addHandler(handler)

    # 降低第三方库日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
