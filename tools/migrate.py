import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from src.core.config import settings  # noqa: E402
from src.core.database import Base, engine  # noqa: E402
from src.models.auth import (Account, Menu, Role, account_roles,  # noqa: E402
                             role_menus)
from src.modules.auth.utils import get_password_hash  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    logger.info("===== 开始创建数据库表 =====")
    logger.info(f"数据库地址: {settings.DATABASE_URL}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("表创建成功！")


async def init_data():
    logger.info("===== 开始初始化数据 =====")

    async with AsyncSession(engine) as session:
        # 1. 创建超级管理员角色
        admin_role = Role(
            name="超级管理员",
            sort=1,
            status=True,
            remark="超级管理员角色，拥有所有权限",
        )
        session.add(admin_role)
        await session.flush()

        # 2. 创建菜单结构（与前端 admin_web/app 目录对应）
        #
        # 前端页面结构:
        # - /login           -> 登录页面（无需权限）
        # - /admin           -> 管理后台布局
        #   - /admin/dashboard -> 仪表盘
        #   - /admin/sys       -> 系统管理目录
        #     - /admin/sys/account -> 账号管理
        #     - /admin/sys/roles   -> 角色管理
        #     - /admin/sys/menu     -> 菜单管理

        # 仪表盘目录
        dashboard_menu = Menu(
            name="仪表盘",
            menu_type=1,
            path="/admin/dashboard",
            component="admin/dashboard/page",
            icon="Dashboard",
            sort=1,
            api_url="",
            api_method="*",
            visible=True,
            status=True,
            pid=0,
            remark="仪表盘目录",
        )
        session.add(dashboard_menu)
        await session.flush()

        # 仪表盘菜单
        dashboard_page = Menu(
            name="数据概览",
            menu_type=2,
            path="/admin/dashboard",
            component="admin/dashboard/page",
            icon="Dashboard",
            sort=1,
            api_url="",
            api_method="*",
            visible=True,
            status=True,
            pid=dashboard_menu.id,
            remark="仪表盘页面",
        )
        session.add(dashboard_page)
        await session.flush()

        # 系统管理目录
        sys_menu = Menu(
            name="系统管理",
            menu_type=1,
            path="/admin/sys",
            component="admin/sys/page",
            icon="Setting",
            sort=2,
            api_url="",
            api_method="*",
            visible=True,
            status=True,
            pid=0,
            remark="系统管理目录",
        )
        session.add(sys_menu)
        await session.flush()

        # 账号管理菜单
        account_menu = Menu(
            name="账号管理",
            menu_type=2,
            path="/admin/sys/account",
            component="admin/sys/account/page",
            icon="Users",
            sort=1,
            api_url="",
            api_method="*",
            visible=True,
            status=True,
            pid=sys_menu.id,
            remark="账号管理菜单",
        )
        session.add(account_menu)
        await session.flush()

        # 角色管理菜单
        role_menu = Menu(
            name="角色管理",
            menu_type=2,
            path="/admin/sys/roles",
            component="admin/sys/roles/page",
            icon="UserRole",
            sort=2,
            api_url="",
            api_method="*",
            visible=True,
            status=True,
            pid=sys_menu.id,
            remark="角色管理菜单",
        )
        session.add(role_menu)
        await session.flush()

        # 菜单管理菜单
        menu_mgmt_menu = Menu(
            name="菜单管理",
            menu_type=2,
            path="/admin/sys/menu",
            component="admin/sys/menu/page",
            icon="Menu",
            sort=3,
            api_url="",
            api_method="*",
            visible=True,
            status=True,
            pid=sys_menu.id,
            remark="菜单管理菜单",
        )
        session.add(menu_mgmt_menu)
        await session.flush()

        # 账号管理按钮
        account_buttons = [
            Menu(
                name="账号列表",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=1,
                api_url="/api/v1/sys/account/list",
                api_method="GET",
                visible=True,
                status=True,
                pid=account_menu.id,
                remark="获取账号列表",
            ),
            Menu(
                name="账号详情",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=2,
                api_url="/api/v1/sys/account/detail",
                api_method="GET",
                visible=True,
                status=True,
                pid=account_menu.id,
                remark="获取账号详情",
            ),
            Menu(
                name="创建账号",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=3,
                api_url="/api/v1/sys/account/create",
                api_method="POST",
                visible=True,
                status=True,
                pid=account_menu.id,
                remark="创建账号",
            ),
            Menu(
                name="更新账号",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=4,
                api_url="/api/v1/sys/account/update",
                api_method="PUT",
                visible=True,
                status=True,
                pid=account_menu.id,
                remark="更新账号",
            ),
            Menu(
                name="删除账号",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=5,
                api_url="/api/v1/sys/account/delete",
                api_method="DELETE",
                visible=True,
                status=True,
                pid=account_menu.id,
                remark="删除账号",
            ),
        ]

        # 角色管理按钮
        role_buttons = [
            Menu(
                name="角色列表",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=1,
                api_url="/api/v1/sys/role/list",
                api_method="GET",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="获取角色列表",
            ),
            Menu(
                name="角色详情",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=2,
                api_url="/api/v1/sys/role/detail",
                api_method="GET",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="获取角色详情",
            ),
            Menu(
                name="创建角色",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=3,
                api_url="/api/v1/sys/role/create",
                api_method="POST",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="创建角色",
            ),
            Menu(
                name="更新角色",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=4,
                api_url="/api/v1/sys/role/update",
                api_method="PUT",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="更新角色",
            ),
            Menu(
                name="删除角色",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=5,
                api_url="/api/v1/sys/role/delete",
                api_method="DELETE",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="删除角色",
            ),
            Menu(
                name="所有角色",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=6,
                api_url="/api/v1/sys/role/all",
                api_method="GET",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="获取所有角色列表",
            ),
            Menu(
                name="关联菜单",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=7,
                api_url="/api/v1/sys/role/associate-menus",
                api_method="POST",
                visible=True,
                status=True,
                pid=role_menu.id,
                remark="关联角色和菜单",
            ),
        ]

        # 菜单管理按钮
        menu_buttons = [
            Menu(
                name="菜单列表",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=1,
                api_url="/api/v1/sys/menu/list",
                api_method="GET",
                visible=True,
                status=True,
                pid=menu_mgmt_menu.id,
                remark="获取菜单列表",
            ),
            Menu(
                name="所有菜单",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=2,
                api_url="/api/v1/sys/menu/all",
                api_method="GET",
                visible=True,
                status=True,
                pid=menu_mgmt_menu.id,
                remark="获取所有菜单列表",
            ),
            Menu(
                name="菜单详情",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=3,
                api_url="/api/v1/sys/menu/detail",
                api_method="GET",
                visible=True,
                status=True,
                pid=menu_mgmt_menu.id,
                remark="获取菜单详情",
            ),
            Menu(
                name="创建菜单",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=4,
                api_url="/api/v1/sys/menu/create",
                api_method="POST",
                visible=True,
                status=True,
                pid=menu_mgmt_menu.id,
                remark="创建菜单",
            ),
            Menu(
                name="更新菜单",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=5,
                api_url="/api/v1/sys/menu/update",
                api_method="PUT",
                visible=True,
                status=True,
                pid=menu_mgmt_menu.id,
                remark="更新菜单",
            ),
            Menu(
                name="删除菜单",
                menu_type=3,
                path="",
                component="",
                icon="",
                sort=6,
                api_url="/api/v1/sys/menu/delete",
                api_method="DELETE",
                visible=True,
                status=True,
                pid=menu_mgmt_menu.id,
                remark="删除菜单",
            ),
        ]

        # 合并所有菜单（目录 + 菜单 + 按钮）
        all_menus = (
            [
                dashboard_menu,
                dashboard_page,
                sys_menu,
                account_menu,
                role_menu,
                menu_mgmt_menu,
            ]
            + account_buttons
            + role_buttons
            + menu_buttons
        )

        for menu in all_menus:
            session.add(menu)
        await session.flush()

        # 3. 将所有菜单分配给超级管理员角色
        for menu in all_menus:
            await session.execute(
                role_menus.insert().values(role_id=admin_role.id, menu_id=menu.id)
            )

        # 4. 创建超级管理员账户
        admin_account = Account(
            name="超级管理员",
            email="admin@example.com",
            password=get_password_hash("123456"),
            status=True,
        )
        session.add(admin_account)
        await session.flush()

        # 5. 将超级管理员角色分配给超级管理员账户
        await session.execute(
            account_roles.insert().values(
                account_id=admin_account.id, role_id=admin_role.id
            )
        )

        # 提交事务
        await session.commit()
        logger.info("数据初始化成功！")
        logger.info("=" * 50)
        logger.info("菜单结构：")
        logger.info("  ├─ /admin/dashboard (仪表盘)")
        logger.info("  │   └─ /admin/dashboard (数据概览)")
        logger.info("  └─ /admin/sys (系统管理)")
        logger.info("      ├─ /admin/sys/account (账号管理, 含 5 个按钮)")
        logger.info("      ├─ /admin/sys/roles (角色管理, 含 7 个按钮)")
        logger.info("      └─ /admin/sys/menu (菜单管理, 含 6 个按钮)")
        logger.info("=" * 50)
        logger.info("默认账号: admin@example.com")
        logger.info("默认密码: 123456")
        logger.info("=" * 50)


async def main():
    # 创建数据库表
    await create_tables()

    # 初始化数据
    await init_data()


# 运行迁移脚本
# PYTHONPATH=. python tools/migrate.py
if __name__ == "__main__":
    asyncio.run(main())
