import json
import logging
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """自定义JSON日志格式化器，将日志输出为标准JSON格式"""

    def format(self, record):
        # 构建基础日志对象，包含核心字段
        log_obj = {
            # UTC时间戳，ISO格式
            "timestamp": datetime.utcnow().isoformat(),
            # 日志级别
            "level": record.levelname,
            # 日志消息内容
            "message": record.getMessage(),
            # 日志器名称
            "logger": record.name,
            # 打印日志的模块名
            "module": record.module,
            # 打印日志的代码行号
            "line": record.lineno,
        }
        # 如果存在异常信息，则添加异常字段
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        # 将日志对象转为JSON字符串返回
        return json.dumps(log_obj)


def setup_logging():
    """配置全局日志格式为JSON，清空默认处理器，输出结构化日志"""
    # 获取根日志器
    root_logger = logging.getLogger()
    # 设置根日志器默认级别为INFO
    root_logger.setLevel(logging.INFO)

    # 移除默认处理器，避免重复日志
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # 创建标准输出流处理器（输出到控制台）
    handler = logging.StreamHandler(sys.stdout)
    # 设置自定义的JSON格式化器
    handler.setFormatter(JSONFormatter())
    # 将处理器添加到根日志器
    root_logger.addHandler(handler)

    # 降低第三方库日志级别，减少冗余输出
    # 关闭uvicorn访问日志噪音
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # 关闭SQLAlchemy执行日志噪音
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
