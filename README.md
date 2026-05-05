# fastapi-admin

基于 FastAPI 和 SQLAlchemy 的轻量级管理后台，支持 RBAC 权限管理、菜单管理和账号管理。

## 功能特性

- **账号管理**：创建、更新、删除账号，账号列表查询
- **角色管理**：创建、更新、删除角色，角色列表查询
- **菜单管理**：支持目录、菜单、按钮三种类型，树形结构
- **权限管理**：基于角色的访问控制（RBAC），支持细粒度权限控制
- **权限中间件**：自动检查用户权限，确保只有授权用户才能访问特定接口
- **双 Token 认证**：Access Token (30分钟) + Refresh Token (7天)，支持 Token 自动刷新
- **数据初始化**：自动创建超级管理员角色、菜单及账户
- **性能优化**：列表查询使用 `selectinload` 解决 N+1 查询问题
- **统一分页**：标准化的分页请求和响应格式
- **CORS 跨域**：开箱即用的跨域资源共享配置
- **GZip 压缩**：减少网络传输体积

## 技术栈

- **后端框架**：FastAPI
- **数据库**：SQLAlchemy 2.0 (异步)
- **认证**：JWT (JSON Web Token)
- **密码加密**：bcrypt
- **依赖管理**：uv

## 安装

```bash
# 克隆项目
git clone https://github.com/chihqiang/fastapi-admin.git
cd fastapi-admin

# 安装skills
npx skills experimental_install
//npx skills add https://github.com/fastapi/fastapi --skill fastapi

# 安装依赖
uv sync

# 执行数据库迁移
alembic upgrade head

# 启动服务
fastapi dev
```

## 快速开始

1. **启动服务**

   ```bash
   fastapi dev
   ```

2. **访问 API 文档**

   浏览器打开 `http://localhost:8000/docs`

3. **默认账号**

   - 邮箱：`admin@example.com`
   - 密码：`123456`

4. **测试 API**

   使用 `api.http` 文件配合 VS Code REST Client 插件进行测试

## 项目结构

```
fastapi-admin/
├── src/
│   ├── boot/                # 启动引导
│   │   ├── __init__.py     # 创建应用实例
│   │   ├── exception.py    # 异常处理
│   │   ├── logger.py       # 日志配置
│   │   ├── middleware.py   # 中间件注册
│   │   └── route.py        # 路由注册
│   ├── core/               # 核心模块
│   │   ├── config.py       # 应用配置
│   │   ├── database.py     # 数据库连接
│   │   ├── dependencies.py  # 依赖注入
│   │   ├── exception.py    # 异常定义
│   │   ├── mail.py         # 邮件发送
│   │   ├── middlewares.py   # 中间件实现
│   │   └── repository.py   # 仓库基类
│   ├── models/             # 数据模型
│   │   └── auth.py         # 认证模型 (Account, Role, Menu)
│   ├── modules/            # 业务模块
│   │   ├── auth/           # 认证模块
│   │   └── sys/            # 系统管理模块
│   │       ├── route.py    # 路由聚合
│   │       ├── account/    # 账号管理
│   │       ├── menu/       # 菜单管理
│   │       └── role/        # 角色管理
│   ├── schemas/            # Pydantic Schema
│   │   ├── pagination.py    # 分页 Schema
│   │   └── response.py      # 响应 Schema
│   └── utils/               # 工具函数
├── alembic/                # 数据库迁移
├── tests/                  # 测试用例
├── api.http               # API 测试文件
├── main.py                # 应用入口
└── pyproject.toml        # 项目配置
```

## 数据模型

### 账号 (Account)

| 字段     | 类型    | 说明             |
|----------|---------|------------------|
| id       | int     | 主键             |
| name     | string  | 用户昵称         |
| email    | string  | 登录邮箱（唯一） |
| password | string  | 加密密码         |
| status   | bool    | 账号是否启用     |

### 角色 (Role)

| 字段   | 类型    | 说明           |
|--------|---------|----------------|
| id     | int     | 主键           |
| name   | string  | 角色名称（唯一）|
| sort   | int     | 显示顺序       |
| status | bool    | 状态           |
| remark | string  | 备注           |

### 菜单 (Menu)

| 字段       | 类型    | 说明                           |
|------------|---------|--------------------------------|
| id         | int     | 主键                           |
| pid        | int     | 父菜单ID                       |
| menu_type  | int     | 菜单类型：1-目录 2-菜单 3-按钮 |
| name       | string  | 菜单名称                       |
| path       | string  | 前端路由地址                   |
| component  | string  | 前端组件路径                   |
| icon       | string  | 菜单图标                       |
| sort       | int     | 显示顺序                       |
| api_url    | string  | 接口地址                       |
| api_method | string  | 请求方式：GET/POST/PUT/DELETE/*|
| visible    | bool    | 是否显示                       |
| status     | bool    | 状态                           |
| remark     | string  | 备注                           |

## 统一响应格式

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

## API 接口

接口文档请参考 `api.http` 文件，可配合 VS Code REST Client 插件使用。

### 认证模块

| 方法 | 路径                     | 说明                       |
|------|--------------------------|----------------------------|
| POST | `/api/v1/auth/register`  | 用户注册                   |
| POST | `/api/v1/auth/login`     | 用户登录，返回双 Token     |
| POST | `/api/v1/auth/refresh`   | 使用 Refresh Token 刷新    |
| GET  | `/api/v1/auth/user/profile`| 获取当前用户信息和权限菜单|

### 账号管理

| 方法 | 路径                         | 说明           |
|------|------------------------------|----------------|
| GET  | `/api/v1/sys/account/list`   | 获取账号列表   |
| GET  | `/api/v1/sys/account/detail` | 获取账号详情   |
| POST | `/api/v1/sys/account/create` | 创建账号       |
| PUT  | `/api/v1/sys/account/update` | 更新账号       |
| DELETE| `/api/v1/sys/account/delete` | 删除账号       |

### 角色管理

| 方法 | 路径                        | 说明               |
|------|-----------------------------|--------------------|
| GET  | `/api/v1/sys/role/list`     | 获取角色列表       |
| GET  | `/api/v1/sys/role/detail`   | 获取角色详情       |
| POST | `/api/v1/sys/role/create`   | 创建角色           |
| PUT  | `/api/v1/sys/role/update`   | 更新角色           |
| DELETE| `/api/v1/sys/role/delete`  | 删除角色           |
| GET  | `/api/v1/sys/role/all`      | 获取所有角色       |
| POST | `/api/v1/sys/role/associate-menus`| 关联角色和菜单|

### 菜单管理

| 方法 | 路径                      | 说明             |
|------|---------------------------|------------------|
| GET  | `/api/v1/sys/menu/list`   | 获取菜单列表     |
| GET  | `/api/v1/sys/menu/all`    | 获取所有菜单     |
| GET  | `/api/v1/sys/menu/detail` | 获取菜单详情     |
| POST | `/api/v1/sys/menu/create` | 创建菜单         |
| PUT  | `/api/v1/sys/menu/update` | 更新菜单         |
| DELETE| `/api/v1/sys/menu/delete`| 删除菜单         |

## 分页规范

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

## 双 Token 认证机制

- **Access Token**：短期有效（30分钟），用于访问受保护接口
- **Refresh Token**：长期有效（7天），用于获取新的 Access Token
- **滚动刷新**：每次刷新时同时生成新的 Access Token 和 Refresh Token

## 数据库迁移 (Alembic)

```bash
# 查看所有迁移
alembic history

# 查看当前版本
alembic current

# 升级到最新版本
alembic upgrade head

# 回滚上一个版本
alembic downgrade -1

# 创建新迁移（自动检测模型变更）
alembic revision --autogenerate -m "描述"
```

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
   from pydantic import BaseModel

   class AccountCreate(BaseModel):
       name: str
       email: str
       password: str
   ```

3. **定义 Router**（`router.py`）

   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix="/account", tags=["账号管理"])

   @router.post("/create")
   async def account_create():
       pass
   ```

4. **注册路由**（在 `src/modules/sys/route.py` 中）

   ```python
   from src.modules.sys.account import router as account_router

   router.include_router(account_router)
   ```

## 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行指定测试文件
uv run pytest tests/test_account.py -v
```

## 注意事项

1. **数据库配置**：默认使用 SQLite 数据库，如需使用其他数据库，请修改 `src/core/config.py`
2. **JWT 密钥**：默认使用开发密钥，生产环境请修改为安全的密钥
3. **安全性**：生产环境请配置 HTTPS，确保数据传输安全

## 许可证

Apache License 2.0
