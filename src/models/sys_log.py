import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SysLog(Base):
    __tablename__ = "sys_logs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键ID"
    )
    uuid: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        comment="UUID全局唯一标识",
    )
    # 请求信息
    request_path: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="请求路径"
    )
    request_method: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="请求方式"
    )
    request_payload: Mapped[str] = mapped_column(Text, nullable=True, comment="请求体")
    request_ip: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="请求IP地址"
    )
    request_os: Mapped[str] = mapped_column(
        String(64), nullable=True, comment="操作系统"
    )
    request_browser: Mapped[str] = mapped_column(
        String(64), nullable=True, comment="浏览器"
    )
    # 响应信息
    response_code: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="响应状态码"
    )
    response_json: Mapped[str] = mapped_column(Text, nullable=True, comment="响应体")
    process_time: Mapped[str] = mapped_column(
        String(20), nullable=True, comment="处理耗时"
    )
    # 接口描述
    description: Mapped[str] = mapped_column(
        String(255), nullable=True, default="", comment="接口描述/备注"
    )
    # 操作用户
    account_id: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="操作用户ID"
    )
    account_name: Mapped[str] = mapped_column(
        String(50), nullable=True, default="", comment="操作用户名"
    )
    # 系统字段
    created_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
