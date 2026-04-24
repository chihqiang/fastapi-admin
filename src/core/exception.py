import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.exc import SQLAlchemyError

from src.schemas.response import fail

logger = logging.getLogger(__name__)


class APIException(Exception):
    """自定义API异常类"""

    def __init__(self, msg: str, code: int = -1, status_code: int = 200):
        self.msg = msg
        self.code = code
        self.status_code = status_code
        super().__init__(self.msg)


class AuthenticationException(APIException):
    """认证失败异常"""

    def __init__(self, msg: str = "授权登录失败，需要重新登录"):
        super().__init__(msg, code=401, status_code=401)


class PermissionException(APIException):
    """权限不足异常"""

    def __init__(self, msg: str = "没有权限"):
        super().__init__(msg, code=403, status_code=403)


def register_exception(app: FastAPI):
    """注册所有异常处理器"""

    # 自定义API异常处理器
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        # 返回统一的错误响应
        return JSONResponse(
            status_code=exc.status_code,
            content=fail(msg=exc.msg, code=exc.code).model_dump(),
        )

    # 全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 记录异常信息
        logger.error(f"Global exception: {exc}", exc_info=True)
        # 返回统一的错误响应
        return JSONResponse(
            status_code=500, content=fail(msg="服务器内部错误", code=500).model_dump()
        )

    # 请求参数验证错误处理器
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # 提取验证错误信息
        error_msg = "参数验证失败: " + ", ".join(
            [f"{field['loc'][-1]}: {field['msg']}" for field in exc.errors()]
        )
        return JSONResponse(
            status_code=422, content=fail(msg=error_msg, code=422).model_dump()
        )

    # 数据库异常处理器
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        # 记录数据库异常
        logger.error(f"Database exception: {exc}", exc_info=True)
        # 将数据库错误信息直接返回给前端
        error_msg = str(exc)
        return JSONResponse(
            status_code=500,
            content=fail(msg=f"数据库操作失败: {error_msg}", code=500).model_dump(),
        )

    # JWT异常处理器
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        return JSONResponse(
            status_code=401, content=fail(msg="认证令牌无效", code=401).model_dump()
        )

    return app
