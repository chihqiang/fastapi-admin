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
