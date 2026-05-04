from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseSchema(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "操作成功"
    data: T | None = None


# 成功返回
def success(data: T = None, msg: str = "操作成功") -> ResponseSchema[T]:
    return ResponseSchema(code=0, msg=msg, data=data)


# 失败返回
def fail(msg: str = "操作失败", code: int = -1, data: T = None) -> ResponseSchema[T]:
    return ResponseSchema(code=code, msg=msg, data=data)
