from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.pagination import PageParams, PageSchema


class MenuId(BaseModel):
    """菜单ID模型"""

    id: int
    name: str | None = None


class RoleBase(BaseModel):
    """角色基础模型"""

    name: str
    sort: int = 0
    status: bool = True
    remark: str = ""

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class RoleCreate(RoleBase):
    """创建角色请求模型"""

    menus: list[MenuId] = Field(default_factory=list)


class RoleUpdate(RoleBase):
    """更新角色请求模型"""

    id: int
    menus: list[MenuId] | None = None


class MenuInfo(BaseModel):
    """菜单信息"""

    id: int
    name: str

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class RoleInfo(RoleBase):
    """角色信息响应模型"""

    id: int
    menus: list[MenuInfo]


class RoleListRequest(PageParams):
    """角色列表请求模型

    继承 PageParams，添加角色特有的查询字段
    """

    id: int | None = Field(default=None, description="角色ID，用于精确搜索")
    name: str | None = Field(default=None, description="角色名称，用于模糊搜索")


class RoleListResponse(PageSchema[RoleInfo]):
    """角色列表响应模型"""

    pass


class RoleDeleteRequest(BaseModel):
    """删除角色请求模型"""

    id: int


class RoleAssociateMenusRequest(BaseModel):
    """关联角色和菜单请求模型"""

    id: int
    menu_ids: list[int]
