from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ==============================
# 请求模型
# ==============================


class RegisterForm(BaseModel):
    """注册请求"""

    name: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=32, description="密码")


class LoginForm(BaseModel):
    """登录请求"""

    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")


class RefreshTokenForm(BaseModel):
    """刷新令牌请求"""

    refresh_token: str = Field(..., description="刷新令牌")


# ==============================
# 响应模型
# ==============================


class RoleInfo(BaseModel):
    """角色信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")


class MenuInfo(BaseModel):
    """菜单信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="菜单ID")
    pid: int = Field(..., description="父菜单ID")
    menu_type: int = Field(..., description="菜单类型")
    name: str = Field(..., description="菜单名称")
    path: str = Field(..., description="路由路径")
    component: str = Field(..., description="组件路径")
    icon: str = Field(..., description="图标")
    sort: int = Field(..., description="排序")
    api_url: str = Field(..., description="API路径")
    api_method: str = Field(..., description="请求方法")
    visible: bool = Field(..., description="是否可见")
    status: bool = Field(..., description="状态")
    remark: str = Field(..., description="备注")


class RegisterOutSchema(BaseModel):
    """注册响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="账户ID")
    name: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")


class LoginOutSchema(BaseModel):
    """登录响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="账户ID")
    name: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")


class RefreshTokenOutSchema(BaseModel):
    """刷新令牌响应"""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")


class ProfileOutSchema(BaseModel):
    """个人资料响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="账户ID")
    name: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    roles: list[RoleInfo] = Field(default_factory=list, description="角色列表")
    menus: list[MenuInfo] = Field(default_factory=list, description="菜单列表")
