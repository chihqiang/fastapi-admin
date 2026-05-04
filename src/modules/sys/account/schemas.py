from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.pagination import PageParams, PageSchema


class RoleId(BaseModel):
    """角色ID模型"""

    id: int
    name: str | None = None


class RoleInfo(BaseModel):
    """角色信息"""

    id: int
    name: str

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class AccountBase(BaseModel):
    """账号基础模型"""

    name: str
    email: str
    status: bool = True

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class AccountCreate(AccountBase):
    """创建账号请求模型"""

    password: str
    roles: list[RoleId] = Field(default_factory=list)


class AccountUpdate(AccountBase):
    """更新账号请求模型"""

    id: int
    password: str | None = None
    roles: list[RoleId] | None = None


class AccountInfo(AccountBase):
    """账号信息响应模型"""

    id: int
    roles: list[RoleInfo]


class AccountListRequest(PageParams):
    """账号列表请求模型

    继承 PageParams，添加账号特有的查询字段
    """

    id: int | None = Field(default=None, description="账号ID，用于精确搜索")


class AccountListResponse(PageSchema[AccountInfo]):
    """账号列表响应模型"""

    pass


class AccountDeleteRequest(BaseModel):
    """删除账号请求模型"""

    id: int
