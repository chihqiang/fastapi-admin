"""
操作日志路由处理器

功能：
- 自动记录 API 请求/响应日志
- 支持配置需记录的 HTTP 方法
- 支持忽略特定接口的日志记录
- 获取客户端 IP、操作系统、浏览器等信息

使用方式：
    在 FastAPI 路由中使用 route_class=SysLogRoute 装饰器即可启用日志记录

配置项（src/core/config.py）：
    - OPERATION_LOG_RECORD: 是否启用操作日志记录
    - OPERATION_RECORD_METHOD: 需要记录的 HTTP 方法列表
    - IGNORE_OPERATION_FUNCTION: 忽略记录日志的接口名称列表
"""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine
from functools import cached_property
from typing import TYPE_CHECKING, Any

from fastapi import Request, Response
from fastapi.routing import APIRoute
from typing_extensions import override

if TYPE_CHECKING:
    from src.handlers.sys_log_handler import SysLogHandler


class SysLogRoute(APIRoute):
    """
    操作日志路由类

    继承自 FastAPI 的 APIRoute，重写路由处理器以实现请求/响应日志记录功能。
    在需要记录日志的路由上使用 route_class=SysLogRoute 即可。
    """

    @cached_property
    def _log_handler(self) -> SysLogHandler:
        """延迟初始化日志处理器"""
        from src.handlers.sys_log_handler import SysLogHandler

        return SysLogHandler()

    @override
    def get_route_handler(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        """
        获取自定义路由处理器

        重写父类方法，在原路由处理之前添加日志记录逻辑。

        Returns:
            Callable: 返回自定义的异步路由处理器函数

        处理流程：
            1. 记录请求开始时间
            2. 执行原路由处理器获取响应
            3. 调用日志处理器记录日志
        """
        original_route_handler = super().get_route_handler()
        log_handler = self._log_handler

        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()
            # 执行原始路由处理器
            response: Response = await original_route_handler(request)
            # 调用日志处理器处理日志
            await log_handler.handle_log(request, response, start_time)
            return response

        return custom_route_handler
