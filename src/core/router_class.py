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

import json
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from fastapi.routing import APIRoute
from user_agents import parse

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.core.instance import token_instance
from src.core.requests import get_bearer_token


class SysLogRoute(APIRoute):
    """
    操作日志路由类

    继承自 FastAPI 的 APIRoute，重写路由处理器以实现请求/响应日志记录功能。
    在需要记录日志的路由上使用 route_class=SysLogRoute 即可。
    """

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
            3. 判断是否需要记录日志
            4. 解析并保存请求/响应信息到数据库
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()
            # 执行原始路由处理器
            response: Response = await original_route_handler(request)
            # 检查是否需要记录日志
            if not self._need_record_log(request):
                return response
            try:
                # ------------------- 1. 解析用户代理信息 -------------------
                user_agent = parse(request.headers.get("user-agent", ""))

                # ------------------- 2. 解析请求体 -------------------
                payload = await self._parse_request_payload(request)

                # ------------------- 3. 解析响应体 -------------------
                response_json = self._parse_response_json(response)

                # ------------------- 4. 计算处理耗时 -------------------
                process_time = f"{(time.time() - start_time):.2f}s"

                # ------------------- 5. 获取操作用户信息 -------------------
                # 优先从请求状态获取（依赖注入已设置），否则从 token 解析
                account_id = getattr(request.state, "account_id", None)
                account_name = getattr(request.state, "account_name", "")
                if not account_id:
                    account_id, account_name = self._get_user_from_token(request)

                # ------------------- 6. 获取客户端真实 IP -------------------
                # 支持代理转发场景下的真实 IP 获取
                request_ip = self._get_real_ip(request)

                # ------------------- 7. 获取路由描述 -------------------
                # 从路由的 summary 获取接口描述
                route = request.scope.get("route")
                description = route.summary if route else ""

                # ------------------- 8. 保存日志到数据库 -------------------
                await self._save_log(
                    request=request,
                    response=response,
                    payload=payload,
                    response_json=response_json,
                    process_time=process_time,
                    account_id=account_id,
                    account_name=account_name,
                    request_ip=request_ip,
                    os_name=str(user_agent.os.family),
                    browser_name=str(user_agent.browser.family),
                    description=description,
                )
            except Exception as e:
                # 日志记录失败不影响正常响应
                logging.error(f"[操作日志记录失败] {str(e)}")

            return response

        return custom_route_handler

    async def _parse_request_payload(self, request: Request) -> str:
        """
        解析请求体内容

        根据不同的 Content-Type 采用不同的解析策略：
        - multipart/form-data: 文件上传，不记录内容
        - application/x-www-form-urlencoded: 表单数据，超长截断
        - application/json: JSON 数据，不截断完整记录
        - 其他: 原始文本，超长截断

        Args:
            request: FastAPI 请求对象

        Returns:
            str: 解析后的请求体字符串
        """
        content_type = request.headers.get("content-type", "").lower()

        # 1. 文件上传 → 跳过，不读取内容
        if "multipart/form-data" in content_type:
            return "文件上传，不记录请求体"

        # 2. URL 编码表单 → 截断防止过长
        if "x-www-form-urlencoded" in content_type:
            form = await request.form()
            payload = str(dict(form))
            return payload[:2000]

        # 3. JSON 或其他文本 → 完整 JSON，文本截断
        body = await request.body()
        try:
            # JSON 数据完整记录
            payload = json.dumps(json.loads(body), ensure_ascii=False)
        except Exception:
            # 非 JSON 文本，截断处理
            payload = body.decode("utf-8", "ignore")[:2000]

        return payload

    def _parse_response_json(self, response: Response) -> str:
        """
        解析响应体内容

        仅记录 JSON 类型的响应体，其他类型返回空字符串。

        Args:
            response: FastAPI 响应对象

        Returns:
            str: JSON 响应体字符串，非 JSON 返回空字符串
        """
        if "application/json" in response.headers.get("Content-Type", ""):
            try:
                return response.body.decode()
            except Exception:
                return ""
        return ""

    def _get_real_ip(self, request: Request) -> str | None:
        """
        获取客户端真实 IP 地址

        优先从 X-Forwarded-For 请求头获取（适用于代理/负载均衡场景），
        其次从请求客户端直接获取。

        Args:
            request: FastAPI 请求对象

        Returns:
            str | None: 客户端 IP 地址
        """
        # 优先从代理头获取（可能有多个 IP，取第一个）
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        # 直接从请求客户端获取
        if request.client:
            return request.client.host

        return None

    def _get_user_from_token(self, request: Request) -> tuple[int | None, str]:
        """
        从请求头 Authorization 中解析用户信息

        由于 SysLogRoute 在依赖注入之前执行，需要直接从 token 中解析用户信息。
        日志记录失败不影响正常请求，异常时返回空信息。

        Args:
            request: FastAPI 请求对象

        Returns:
            tuple[int | None, str]: (account_id, account_name)
        """
        try:
            token = get_bearer_token(request)
            payload = token_instance.verify_token(token)
            if not payload:
                return None, ""
            return payload.id, ""
        except Exception:
            return None, ""

    def _need_record_log(self, request: Request) -> bool:
        """
        判断当前请求是否需要记录日志

        根据以下条件综合判断：
        1. 全局开关是否启用
        2. 请求方法是否在记录白名单中
        3. 接口名称是否在忽略黑名单中

        Args:
            request: FastAPI 请求对象

        Returns:
            bool: True 需要记录，False 跳过记录
        """
        # 检查全局开关
        if not settings.OPERATION_LOG_RECORD:
            return False

        # 检查 HTTP 方法
        if request.method not in settings.OPERATION_RECORD_METHOD:
            return False

        # 检查是否在忽略列表中
        route = request.scope.get("route")
        if route and route.name in settings.IGNORE_OPERATION_FUNCTION:
            return False

        return True

    async def _save_log(
        self,
        request: Request,
        response: Response,
        payload: str,
        response_json: str,
        process_time: str,
        account_id: int | None,
        account_name: str | None,
        request_ip: str | None,
        os_name: str,
        browser_name: str,
        description: str | None,
    ) -> None:
        """
        保存操作日志到数据库

        使用独立的数据库会话异步保存日志，不影响主请求响应。

        Args:
            request: FastAPI 请求对象
            response: FastAPI 响应对象
            payload: 请求体内容
            response_json: 响应体内容
            process_time: 请求处理耗时
            account_id: 操作用户 ID
            account_name: 操作用户名称
            request_ip: 请求来源 IP
            os_name: 客户端操作系统
            browser_name: 客户端浏览器
            description: 接口描述/备注
        """
        from src.modules.sys.log.schemas import LogCreate
        from src.modules.sys.log.service import LogService

        async with AsyncSessionLocal() as session:
            log_service = LogService(session)
            _ = await log_service.create(
                LogCreate(
                    request_path=request.url.path,
                    request_method=request.method,
                    request_payload=payload,
                    request_ip=request_ip,
                    request_os=os_name,
                    request_browser=browser_name,
                    response_code=response.status_code,
                    response_json=response_json,
                    process_time=process_time,
                    account_id=account_id,
                    account_name=account_name,
                    description=description,
                )
            )
