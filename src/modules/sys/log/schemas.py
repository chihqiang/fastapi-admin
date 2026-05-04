from typing import ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.pagination import PageParams, PageSchema


class LogBase(BaseModel):
    """日志基础模型"""

    request_path: str
    request_method: str
    response_code: int

    request_payload: Optional[str] = None
    request_ip: Optional[str] = None
    request_os: Optional[str] = None
    request_browser: Optional[str] = None
    response_json: Optional[str] = None
    process_time: Optional[str] = None
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    description: Optional[str] = None
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class LogListRequest(PageParams):
    """日志列表请求模型

    继承 PageParams，添加日志特有的查询字段
    """

    id: int | None = Field(default=None, description="日志ID，用于精确搜索")
    request_ip: str | None = Field(default=None, description="请求IP，模糊搜索")
    account_id: int | None = Field(default=None, description="账号ID，用于精确搜索")
    request_method: str | None = Field(default=None, description="请求方法，精确搜索")
    request_path: str | None = Field(default=None, description="请求路径，模糊搜索")


class LogItem(LogBase):
    """日志项模型，包含 ID"""

    id: int = Field(description="日志ID")


class LogListResponse(PageSchema[LogItem]):
    """日志列表响应模型"""

    pass


class LogCreate(LogBase):
    """创建日志请求模型"""

    pass
