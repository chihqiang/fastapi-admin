from pydantic import BaseModel, EmailStr


# 角色信息
class RoleInfo(BaseModel):
    """角色信息"""

    id: int
    name: str


# 菜单信息
class MenuInfo(BaseModel):
    """菜单信息"""

    id: int
    pid: int
    menu_type: int
    name: str
    path: str
    component: str
    icon: str
    sort: int
    api_url: str
    api_method: str
    visible: bool
    status: bool
    remark: str


# 注册请求体
class RegisterForm(BaseModel):
    name: str
    email: EmailStr
    password: str


# 登录请求体
class LoginForm(BaseModel):
    email: EmailStr
    password: str


# 刷新 Token 请求体
class RefreshTokenForm(BaseModel):
    refresh_token: str
