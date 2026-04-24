from typing import List, Optional

from pydantic import BaseModel, Field

from src.schemas.pagination import PageParams, PageResponse


class RoleId(BaseModel):
    """角色ID模型"""

    id: int
    name: Optional[str] = None


class RoleInfo(BaseModel):
    """角色信息"""

    id: int
    name: str

    model_config = {"from_attributes": True}


class AccountBase(BaseModel):
    """账号基础模型"""

    name: str
    email: str
    status: bool = True

    model_config = {"from_attributes": True}


class AccountCreate(AccountBase):
    """创建账号请求模型"""

    password: str
    roles: List[RoleId] = Field(default_factory=list)


class AccountUpdate(AccountBase):
    """更新账号请求模型"""

    id: int
    password: Optional[str] = None
    roles: Optional[List[RoleId]] = None


class AccountInfo(AccountBase):
    """账号信息响应模型"""

    id: int
    roles: List[RoleInfo]


class AccountListRequest(PageParams):
    """账号列表请求模型

    继承 PageParams，添加账号特有的查询字段
    """

    id: Optional[int] = Field(default=None, description="账号ID，用于精确搜索")


class AccountListResponse(PageResponse[AccountInfo]):
    """账号列表响应模型"""

    pass


class AccountDeleteRequest(BaseModel):
    """删除账号请求模型"""

    id: int
