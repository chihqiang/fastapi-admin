"""
全局异常处理器注册模块

注册各种类型的异常处理器，提供统一的错误响应格式
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.exc import SQLAlchemyError

from src.core.exception import APIException
from src.schemas.response import fail


def register_exception(app: FastAPI) -> None:
    """注册所有异常处理器"""
    logging.info("📝 注册异常处理器...")

    # 自定义API异常处理器
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logging.warning(f"API异常: {request.url.path} - {exc.msg}")
        return JSONResponse(
            status_code=exc.status_code,
            content=fail(msg=exc.msg, code=exc.code).model_dump(),
        )

    # 全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logging.error(
            f"全局异常 [{request.method} {request.url.path}]: {exc}", exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=fail(msg="服务器内部错误", code=500).model_dump(),
        )

    # 请求参数验证错误处理器
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = exc.errors()
        error_fields = [f"{e['loc'][-1]}" for e in errors]
        error_msg = "参数验证失败: " + ", ".join(error_fields)
        logging.warning(
            f"验证错误 [{request.method} {request.url.path}]: {error_fields}"
        )
        return JSONResponse(
            status_code=422,
            content=fail(msg=error_msg, code=422).model_dump(),
        )

    # 数据库异常处理器
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logging.error(
            f"数据库异常 [{request.method} {request.url.path}]: {exc}", exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=fail(msg="数据库操作失败", code=500).model_dump(),
        )

    # JWT异常处理器
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        logging.warning(f"JWT认证失败 [{request.method} {request.url.path}]: {exc}")
        return JSONResponse(
            status_code=401,
            content=fail(msg="认证令牌无效", code=401).model_dump(),
        )
