"""
全局异常处理器注册模块

注册各种类型的异常处理器，提供统一的错误响应格式
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from src.core.exception import APIException
from src.schemas.response import fail


def register_exception(app: FastAPI) -> None:
    """注册所有异常处理器"""
    logging.info("📝 注册异常处理器...")

    # 自定义API异常处理器
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logging.warning(
            f"[自定义异常] {request.method} {request.url.path} | 错误码: {exc.code} | 错误信息: {exc.msg}"
        )
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=fail(
                msg="服务器内部错误", code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def HttpExceptionHandler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """
        HTTP异常处理器

        参数:
        - request (Request): 请求对象。
        - exc (HTTPException): HTTP异常实例。

        返回:
        - JSONResponse: 包含错误信息的 JSON 响应。
        """
        logging.error(
            f"[HTTP异常] {request.method} {request.url.path} | 状态码: {exc.status_code} | 错误信息: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=fail(msg=exc.detail, code=exc.status_code).model_dump(),
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=fail(
                msg=error_msg, code=status.HTTP_422_UNPROCESSABLE_CONTENT
            ).model_dump(),
        )

    @app.exception_handler(ResponseValidationError)
    async def ResponseValidationHandle(
        request: Request, exc: ResponseValidationError
    ) -> JSONResponse:
        """
        响应参数验证异常处理器

        参数:
        - request (Request): 请求对象。
        - exc (ResponseValidationError): 响应参数验证异常实例。

        返回:
        - JSONResponse: 包含错误信息的 JSON 响应。
        """
        logging.error(
            f"[响应验证异常] {request.method} {request.url.path} | 错误信息: 响应数据格式错误 | 详情: {exc.errors()}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=fail(
                msg=exc.body, code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump(),
        )

    # 数据库异常处理器
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        error_msg = "数据库操作失败"
        exc_type = type(exc).__name__
        logging.error(
            f"数据库异常 [{request.method} {request.url.path}]: {exc}", exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=fail(
                msg=f"{error_msg}: {exc_type}", code=status.HTTP_400_BAD_REQUEST
            ).model_dump(),
        )

    @app.exception_handler(ValueError)
    async def ValueExceptionHandler(request: Request, exc: ValueError) -> JSONResponse:
        """
        值异常处理器

        参数:
        - request (Request): 请求对象。
        - exc (ValueError): 值异常实例。

        返回:
        - JSONResponse: 包含错误信息的 JSON 响应。
        """
        logging.error(
            f"[值异常] {request.method} {request.url.path} | 错误信息: {exc!s}"
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=fail(msg=str(exc), code=status.HTTP_400_BAD_REQUEST).model_dump(),
        )

    # JWT异常处理器
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        logging.warning(f"JWT认证失败 [{request.method} {request.url.path}]: {exc}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=fail(
                msg="认证令牌无效", code=status.HTTP_401_UNAUTHORIZED
            ).model_dump(),
        )
