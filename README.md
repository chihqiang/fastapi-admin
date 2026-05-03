# fastapi-admin

A lightweight admin dashboard built with FastAPI and SQLAlchemy, featuring role-based access control (RBAC), menu management, and account management.

## 功能特性

- **账号管理**：支持创建、更新、删除账号，以及账号列表查询
- **角色管理**：支持创建、更新、删除角色，以及角色列表查询
- **菜单管理**：支持创建、更新、删除菜单，以及菜单列表查询
- **权限管理**：基于角色的访问控制（RBAC），支持细粒度的权限控制
- **权限中间件**：自动检查用户权限，确保只有授权用户才能访问特定接口
- **双 Token 认证**：Access Token (30分钟) + Refresh Token (7天)，支持 Token 自动刷新
- **数据初始化**：自动创建超级管理员角色、菜单及账户
- **性能优化**：列表查询使用 `selectinload` 解决 N+1 查询问题
- **统一分页**：标准化的分页请求和响应格式

## 技术栈

- **后端框架**：FastAPI
- **数据库**：SQLAlchemy 2.0 (支持异步)
- **认证**：JWT (JSON Web Token)
- **依赖管理**：uv

## 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/chihqiang/fastapi-admin.git
   cd fastapi-admin
   ```

2. **安装依赖**

    ```bash
    uv install
    ```

3. **创建数据库**
   - 默认使用 SQLite 数据库，无需额外配置
   - 如需使用其他数据库，请修改 `src/core/config.py` 中的数据库连接字符串

4. **数据库迁移**

   ```bash
   # 执行所有迁移
   alembic upgrade head

   # 查看当前版本
   alembic current

   # 查看迁移历史
   alembic history
   ```

## 快速开始

1. **启动开发服务器**

   ```bash
   python main.py
   ```

2. **访问 API 文档**
   - 打开浏览器，访问 `http://localhost:8000/docs`

3. **登录系统**
   - 账号：`admin@example.com`
   - 密码：`123456`

4. **测试 API**
   - 使用 `api.http` 文件配合 VS Code REST Client 插件进行测试
   - 或使用 Postman/curl 等工具

## 项目结构

```bash
fastapi-admin/
├── src/
│   ├── core/            # 核心配置和工具
│   │   ├── config.py    # 配置文件
│   │   ├── database.py  # 数据库连接
│   │   ├── exception.py # 异常处理
│   │   ├── logger.py    # 日志配置
│   │   └── repository.py # 通用 Repository
│   ├── models/          # 数据模型
│   │   └── auth.py      # 认证相关模型（Account, Role, Menu）
│   ├── modules/         # 业务模块
│   │   ├── auth/        # 认证模块
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── sys/         # 系统管理模块
│   │       ├── account/ # 账号管理
│   │       ├── menu/    # 菜单管理
│   │       └── role/    # 角色管理
│   ├── schemas/         # 共享 Schema
│   │   ├── pagination.py # 通用分页 Schema
│   │   └── response.py  # 统一响应 Schema
│   └── __init__.py
├── storage/             # 存储目录
├── api.http             # API 测试文件
├── main.py              # 应用入口
├── pyproject.toml       # 项目配置
└── README.md            # 项目文档
```

## 数据模型

### 账号 (Account)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | string | 用户昵称/姓名 |
| email | string | 登录邮箱（唯一） |
| password | string | 加密密码 |
| status | bool | 账号是否启用 |

### 角色 (Role)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | string | 角色名称（唯一） |
| sort | int | 显示顺序 |
| status | bool | 状态 |
| remark | string | 备注 |

### 菜单 (Menu)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| pid | int | 父菜单ID |
| menu_type | int | 菜单类型：1-目录 2-菜单 3-按钮 |
| name | string | 菜单名称 |
| path | string | 前端路由地址 |
| component | string | 前端组件路径 |
| icon | string | 菜单图标 |
| sort | int | 显示顺序 |
| api_url | string | 接口地址 |
| api_method | string | 请求方式：GET/POST/PUT/DELETE/* |
| visible | bool | 是否显示 |
| status | bool | 状态 |
| remark | string | 备注 |

## API 文档

### 统一响应格式

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

### 错误响应

```json
{
  "code": 400,
  "msg": "错误信息",
  "data": null
}
```

---

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录，返回双 Token |
| POST | `/api/v1/auth/refresh` | 使用 Refresh Token 获取新的 Access Token |
| GET | `/api/v1/auth/user/profile` | 获取当前登录用户信息和权限菜单 |

#### 注册

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "测试用户",
  "email": "test@example.com",
  "password": "123456"
}
```

#### 登录

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "123456"
}
```

**响应示例**：
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "id": 1,
    "name": "管理员",
    "email": "admin@example.com",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 30
  }
}
```

#### Token 刷新

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

#### 获取用户信息

```bash
GET /api/v1/auth/user/profile
Authorization: Bearer {access_token}
```

---

### 分页规范

所有列表接口使用统一的分页格式：

**请求参数**：
- `page`: 页码，从 1 开始，默认 1
- `size`: 每页数量，默认 10，最大 100

**响应格式**：
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "data": [...],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10
  }
}
```

---

### 账号管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/sys/account/list` | 获取账号列表（分页） |
| GET | `/api/v1/sys/account/detail?id=1` | 获取账号详情 |
| POST | `/api/v1/sys/account/create` | 创建账号 |
| PUT | `/api/v1/sys/account/update` | 更新账号 |
| DELETE | `/api/v1/sys/account/delete?id=1` | 删除账号 |

#### 账号列表

```bash
GET /api/v1/sys/account/list?page=1&size=10&id=1
Authorization: Bearer {access_token}
```

**响应示例**：
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "data": [
      {
        "id": 1,
        "name": "管理员",
        "email": "admin@example.com",
        "status": true,
        "roles": [
          {"id": 1, "name": "超级管理员"}
        ]
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

#### 创建账号

```bash
POST /api/v1/sys/account/create
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "新用户",
  "email": "new@example.com",
  "password": "123456",
  "status": true,
  "roles": [
    {"id": 1, "name": "超级管理员"}
  ]
}
```

#### 更新账号

```bash
PUT /api/v1/sys/account/update
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "id": 1,
  "name": "超级管理员",
  "email": "admin@example.com",
  "status": true,
  "roles": []
}
```

#### 删除账号

```bash
DELETE /api/v1/sys/account/delete?id=1
Authorization: Bearer {access_token}
```

---

### 角色管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/sys/role/list` | 获取角色列表（分页，支持 name 模糊搜索） |
| GET | `/api/v1/sys/role/detail?id=1` | 获取角色详情 |
| POST | `/api/v1/sys/role/create` | 创建角色 |
| PUT | `/api/v1/sys/role/update` | 更新角色 |
| DELETE | `/api/v1/sys/role/delete?id=1` | 删除角色 |
| GET | `/api/v1/sys/role/all` | 获取所有角色列表（不分页） |
| POST | `/api/v1/sys/role/associate-menus` | 关联角色和菜单 |

#### 角色列表

```bash
GET /api/v1/sys/role/list?page=1&size=10&name=管理
Authorization: Bearer {access_token}
```

**响应示例**：
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "data": [
      {
        "id": 1,
        "name": "超级管理员",
        "sort": 0,
        "status": true,
        "remark": "系统超级管理员",
        "menus": [
          {"id": 1, "name": "系统管理"}
        ]
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

#### 创建角色

```bash
POST /api/v1/sys/role/create
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "普通用户",
  "sort": 1,
  "status": true,
  "remark": "普通用户角色",
  "menus": [
    {"id": 1, "name": "系统管理"}
  ]
}
```

#### 更新角色

```bash
PUT /api/v1/sys/role/update
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "id": 1,
  "name": "超级管理员",
  "sort": 0,
  "status": true,
  "remark": "系统超级管理员",
  "menus": []
}
```

#### 关联角色和菜单

```bash
POST /api/v1/sys/role/associate-menus
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "id": 1,
  "menu_ids": [1, 2, 3, 4, 5]
}
```

---

### 菜单管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/sys/menu/list` | 获取菜单列表（分页，支持 name 模糊搜索） |
| GET | `/api/v1/sys/menu/all` | 获取所有菜单列表（不分页） |
| GET | `/api/v1/sys/menu/detail?id=1` | 获取菜单详情 |
| POST | `/api/v1/sys/menu/create` | 创建菜单 |
| PUT | `/api/v1/sys/menu/update` | 更新菜单 |
| DELETE | `/api/v1/sys/menu/delete?id=1` | 删除菜单 |

#### 菜单列表

```bash
GET /api/v1/sys/menu/list?page=1&size=10&name=系统&status=true
Authorization: Bearer {access_token}
```

**响应示例**：
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "pid": 0,
        "menu_type": 1,
        "name": "系统管理",
        "path": "/system",
        "component": "Layout",
        "icon": "Setting",
        "sort": 1,
        "api_url": "",
        "api_method": "*",
        "visible": true,
        "status": true,
        "remark": "系统管理",
        "children": []
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

#### 创建菜单（目录）

```bash
POST /api/v1/sys/menu/create
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "系统管理",
  "menu_type": 1,
  "path": "/system",
  "component": "Layout",
  "icon": "Setting",
  "sort": 1,
  "api_url": "",
  "api_method": "*",
  "visible": true,
  "status": true,
  "pid": null,
  "remark": "系统管理目录"
}
```

#### 创建菜单（菜单）

```bash
POST /api/v1/sys/menu/create
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "账号管理",
  "menu_type": 2,
  "path": "/system/account",
  "component": "/system/account/index",
  "icon": "User",
  "sort": 1,
  "api_url": "",
  "api_method": "*",
  "visible": true,
  "status": true,
  "pid": 1,
  "remark": "账号管理菜单"
}
```

#### 创建菜单（按钮）

```bash
POST /api/v1/sys/menu/create
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "新增账号",
  "menu_type": 3,
  "path": "",
  "component": "",
  "icon": "",
  "sort": 1,
  "api_url": "/api/v1/sys/account/create",
  "api_method": "POST",
  "visible": true,
  "status": true,
  "pid": 2,
  "remark": "新增账号按钮"
}
```

#### 更新菜单

```bash
PUT /api/v1/sys/menu/update
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "id": 1,
  "name": "系统管理中心",
  "menu_type": 1,
  "path": "/system",
  "component": "Layout",
  "icon": "Settings",
  "sort": 0,
  "api_url": "",
  "api_method": "*",
  "visible": true,
  "status": true,
  "pid": null,
  "remark": "系统管理中心"
}
```

---

## 权限管理

### 权限检查流程

1. **用户登录**：获取 JWT Access Token 和 Refresh Token
2. **请求接口**：在请求头中携带 Access Token：`Authorization: Bearer {access_token}`
3. **权限检查**：中间件自动检查用户权限
4. **授权访问**：如果用户有权限，允许访问；否则返回 403 错误

### 权限配置

- **菜单配置**：在创建菜单时，设置 `api_url` 和 `api_method`
- **角色配置**：为角色关联相应的菜单
- **账号配置**：为账号关联相应的角色

## 技术实现细节

### 双 Token 认证机制

- **Access Token**：短期有效（30分钟），用于访问受保护接口
- **Refresh Token**：长期有效（7天），用于获取新的 Access Token
- **滚动刷新**：每次刷新时同时生成新的 Access Token 和 Refresh Token

### 分页实现

通用分页 Schema 定义在 `src/schemas/pagination.py`：

```python
# 请求参数继承 PageParams
class AccountListRequest(PageParams):
    id: Optional[int] = None  # 特有查询字段

# 响应继承 PageResponse
class AccountListResponse(PageResponse[AccountInfo]):
    pass
```

### N+1 查询优化

列表查询使用 `selectinload` 替代懒加载，避免 N+1 问题：

```python
# 列表查询 - 使用 selectinload（并行加载）
stmt = select(Account).options(selectinload(Account.roles))

# 单条查询 - 使用 joinedload（连表查询）
stmt = select(Account).options(joinedload(Account.roles))
```

## 数据初始化

运行 `python tools/migrate.py` 脚本，会自动执行以下操作：

1. **创建数据库表**：根据模型创建数据库表结构
2. **创建超级管理员角色**：拥有所有权限
3. **创建菜单**：包含所有系统接口
4. **关联角色和菜单**：将所有菜单分配给超级管理员角色
5. **创建超级管理员账户**：账号 `admin@example.com`，密码 `123456`

## 开发指南

### 添加新的业务模块

以添加账号模块为例：

1. **创建目录结构**

   ```
   src/modules/sys/account/
   ├── __init__.py
   ├── router.py
   ├── schemas.py
   ├── service.py
   └── repository.py
   ```

2. **定义 Schema**（`schemas.py`）

   ```python
   from typing import List, Optional
   from pydantic import BaseModel

   class AccountBase(BaseModel):
       name: str
       email: str
       status: bool = True

   class AccountCreate(AccountBase):
       password: str

   class AccountInfo(AccountBase):
       id: int
       roles: List[RoleInfo] = []
   ```

3. **定义 Service**（`service.py`）

   ```python
   async def create_account(data: AccountCreate, db: AsyncSession) -> AccountInfo:
       # 业务逻辑
       pass
   ```

4. **定义 Router**（`router.py`）

   ```python
   router = APIRouter(prefix="/account", tags=["账号管理"])

   @router.post("/create")
   async def account_create(data: AccountCreate, db: AsyncSession = Depends(get_db)):
       result = await create_account(data, db)
       return success(data=result)
   ```

5. **注册路由**（在 `main.py` 或 `__init__.py` 中）

   ```python
   from src.modules.sys.account.router import router as account_router
   app.include_router(account_router, prefix="/api/v1/sys")
   ```

### 使用 VS Code REST Client 测试

项目包含 `api.http` 文件，可直接在 VS Code 中使用 REST Client 插件进行 API 测试：

1. 安装 REST Client 插件
2. 打开 `api.http` 文件
3. 点击请求上方的 "Send Request" 链接

## 数据库迁移 (Alembic)

本项目使用 [Alembic](https://alembic.sqlalchemy.org/) 进行数据库版本管理。

### 常用命令

```bash
# 查看所有迁移
alembic history

# 查看当前版本
alembic current

# 升级到最新版本
alembic upgrade head

# 回滚上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision>

# 创建新迁移（空迁移）
alembic revision -m "add new table"

# 创建新迁移（自动检测模型变更）
alembic revision --automerge -m "update table"

# 检查迁移脚本是否有问题
alembic check

# 查看指定版本的详细信息
alembic show <revision>
```

### 迁移工作流程

1. **修改模型**：在 `src/models/` 下修改或新增数据模型
2. **生成迁移**：运行 `alembic revision --automerate -m "描述"`
3. **检查迁移**：运行 `alembic check` 确认无误
4. **执行迁移**：运行 `alembic upgrade head` 应用更改
5. **如需回滚**：运行 `alembic downgrade -1` 回滚上一个版本

### 迁移文件位置

迁移文件位于 `alembic/versions/` 目录下，每个迁移文件都有唯一的版本 ID。

## 注意事项

1. **数据库配置**：默认使用 SQLite 数据库，如需使用其他数据库，请修改 `src/core/config.py` 中的数据库连接字符串
2. **JWT 密钥**：默认使用开发密钥，生产环境请修改为安全的密钥
3. **权限管理**：确保为每个接口设置正确的 `api_url` 和 `api_method`
4. **安全性**：生产环境请配置 HTTPS，确保数据传输安全
5. **Token 安全**：Refresh Token 应安全存储，避免泄露

## 许可证

Apache License 2.0
