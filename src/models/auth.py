from typing import List

from sqlalchemy import Column, ForeignKey, Index, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

# 角色-菜单 多对多关联表
role_menus = Table(
    "sys_role_menus",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("sys_roles.id"),
        primary_key=True,
        comment="角色ID",
    ),
    Column(
        "menu_id",
        Integer,
        ForeignKey("sys_menus.id"),
        primary_key=True,
        comment="菜单ID",
    ),
    comment="角色-菜单关联表",
)

# 用户-角色 多对多关联表
account_roles = Table(
    "sys_account_roles",
    Base.metadata,
    Column(
        "account_id",
        Integer,
        ForeignKey("sys_accounts.id"),
        primary_key=True,
        comment="用户ID",
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("sys_roles.id"),
        primary_key=True,
        comment="角色ID",
    ),
    comment="用户-角色关联表",
)


class Menu(Base):
    """菜单表"""

    __tablename__ = "sys_menus"
    __table_args__ = (
        Index("idx_menu_pid", "pid"),
        Index("idx_menu_status", "status"),
        {"comment": "菜单表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment="菜单ID")
    pid: Mapped[int] = mapped_column(default=0, comment="父菜单ID")
    menu_type: Mapped[int] = mapped_column(
        nullable=False, comment="菜单类型：1-目录 2-菜单 3-按钮"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="菜单名称")
    path: Mapped[str] = mapped_column(String(255), default="", comment="前端路由地址")
    component: Mapped[str] = mapped_column(
        String(255), default="", comment="前端组件路径"
    )
    icon: Mapped[str] = mapped_column(String(100), default="", comment="菜单图标")
    sort: Mapped[int] = mapped_column(default=0, comment="显示顺序")
    api_url: Mapped[str] = mapped_column(String(255), default="", comment="接口地址")
    api_method: Mapped[str] = mapped_column(
        String(10), default="*", comment="请求方式：GET/POST/PUT/DELETE/*"
    )
    visible: Mapped[bool] = mapped_column(default=True, comment="是否显示")
    status: Mapped[bool] = mapped_column(
        default=True, comment="状态：true-正常 false-禁用"
    )
    remark: Mapped[str] = mapped_column(String(500), default="", comment="备注")

    # 反向关联角色
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_menus, back_populates="menus"
    )


class Role(Base):
    """角色表"""

    __tablename__ = "sys_roles"
    __table_args__ = {"comment": "角色表"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment="主键ID")
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="角色名称"
    )
    sort: Mapped[int] = mapped_column(default=0, comment="显示顺序")
    status: Mapped[bool] = mapped_column(
        default=True, comment="状态：true-正常 false-禁用"
    )
    remark: Mapped[str] = mapped_column(String(500), default="", comment="备注")

    # 多对多：角色绑定菜单
    menus: Mapped[List["Menu"]] = relationship(
        secondary=role_menus, back_populates="roles"
    )
    # 多对多：角色绑定用户
    accounts: Mapped[List["Account"]] = relationship(
        secondary=account_roles, back_populates="roles"
    )


class Account(Base):
    """账号/用户表"""

    __tablename__ = "sys_accounts"
    __table_args__ = (
        Index("idx_account_email", "email", unique=True),
        Index("idx_account_status", "status"),
        {"comment": "账号表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment="主键ID")
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="用户昵称/姓名"
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False, comment="登录邮箱"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="加密密码"
    )
    status: Mapped[bool] = mapped_column(default=True, comment="账号是否启用")

    # 多对多：用户绑定多个角色
    roles: Mapped[list["Role"]] = relationship(
        secondary=account_roles, back_populates="accounts"
    )
