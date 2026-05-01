"""通用分页 Schema

提供统一的分页请求参数和响应模型，所有列表接口应复用这些基础模型。
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PageParams(BaseModel):
    """分页请求参数基类

    所有列表查询请求应继承此类，可添加自定义查询字段。

    Example:
        >>> class UserListRequest(PageParams):
        ...     name: Optional[str] = None
        ...     status: Optional[bool] = None
    """

    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")

    @property
    def offset(self) -> int:
        """计算 SQL 查询的 offset 值"""
        return (self.page - 1) * self.size


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型基类

    所有列表查询响应应使用此模型，通过泛型指定 items 的数据类型。

    Example:
        >>> class UserListResponse(PageResponse[UserInfo]):
        ...     pass
        >>>
        >>> # 直接构造，pages 自动计算
        >>> response = UserListResponse(data=user_list, total=100, page=1, size=10)
    """

    data: list[T] = Field(description="数据列表")
    total: int = Field(ge=0, description="总记录数")
    page: int = Field(ge=1, description="当前页码")
    size: int = Field(ge=1, description="每页数量")

    @computed_field
    @property
    def pages(self) -> int:
        """总页数，自动计算"""
        return (self.total + self.size - 1) // self.size if self.size > 0 else 0
