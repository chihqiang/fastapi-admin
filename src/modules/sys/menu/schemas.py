from typing import List, Optional

from pydantic import BaseModel, Field

from src.schemas.pagination import PageParams, PageResponse


class MenuBase(BaseModel):
    """菜单基础模型"""

    name: str
    menu_type: int = Field(ge=1, le=3, description="菜单类型：1-目录 2-菜单 3-按钮")
    path: str
    component: str = ""
    icon: str = ""
    sort: int = 0
    api_url: str = ""
    api_method: str = "*"
    visible: bool = True
    status: bool = True
    pid: Optional[int] = None
    remark: str = ""

    model_config = {"from_attributes": True}


class MenuCreate(MenuBase):
    """创建菜单请求模型"""

    pass


class MenuUpdate(MenuBase):
    """更新菜单请求模型"""

    id: int


class MenuInfo(MenuBase):
    """菜单信息响应模型"""

    id: int
    children: List["MenuInfo"] = []


class MenuListRequest(PageParams):
    """菜单列表请求模型

    继承 PageParams，添加菜单特有的查询字段
    """

    id: Optional[int] = Field(default=None, description="菜单ID，用于精确搜索")
    name: Optional[str] = Field(default=None, description="菜单名称，用于模糊搜索")
    status: Optional[bool] = Field(default=None, description="状态筛选")


class MenuListResponse(PageResponse[MenuInfo]):
    """菜单列表响应模型"""

    pass


class MenuDeleteRequest(BaseModel):
    """删除菜单请求模型"""

    id: int
