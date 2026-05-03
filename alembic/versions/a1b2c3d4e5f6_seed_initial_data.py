"""seed initial data

Revision ID: a1b2c3d4e5f6
Revises: c6c4b787c863
Create Date: 2026-05-03 15:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import bcrypt


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'c6c4b787c863'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """插入初始数据（与 migrate.py 保持一致）"""
    password_hash = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()

    # 1. 超级管理员角色
    op.execute("""
        INSERT INTO sys_roles (id, name, sort, status, remark)
        VALUES (1, '超级管理员', 1, 1, '超级管理员角色，拥有所有权限')
    """)

    # 2. 菜单结构
    op.execute("""
        INSERT INTO sys_menus (id, pid, menu_type, name, path, component, icon, sort, api_url, api_method, visible, status, remark)
        VALUES
        (1, 0, 1, '仪表盘', '/admin/dashboard', 'admin/dashboard/page', 'Dashboard', 1, '', '*', 1, 1, '仪表盘目录'),
        (2, 1, 2, '数据概览', '/admin/dashboard', 'admin/dashboard/page', 'Dashboard', 1, '', '*', 1, 1, '仪表盘页面'),
        (3, 0, 1, '系统管理', '/admin/sys', 'admin/sys/page', 'Setting', 2, '', '*', 1, 1, '系统管理目录'),
        (4, 3, 2, '账号管理', '/admin/sys/account', 'admin/sys/account/page', 'Users', 1, '', '*', 1, 1, '账号管理菜单'),
        (5, 3, 2, '角色管理', '/admin/sys/roles', 'admin/sys/roles/page', 'UserRole', 2, '', '*', 1, 1, '角色管理菜单'),
        (6, 3, 2, '菜单管理', '/admin/sys/menu', 'admin/sys/menu/page', 'Menu', 3, '', '*', 1, 1, '菜单管理菜单'),
        (7, 4, 3, '账号列表', '', '', '', 1, '/api/v1/sys/account/list', 'GET', 1, 1, '获取账号列表'),
        (8, 4, 3, '账号详情', '', '', '', 2, '/api/v1/sys/account/detail', 'GET', 1, 1, '获取账号详情'),
        (9, 4, 3, '创建账号', '', '', '', 3, '/api/v1/sys/account/create', 'POST', 1, 1, '创建账号'),
        (10, 4, 3, '更新账号', '', '', '', 4, '/api/v1/sys/account/update', 'PUT', 1, 1, '更新账号'),
        (11, 4, 3, '删除账号', '', '', '', 5, '/api/v1/sys/account/delete', 'DELETE', 1, 1, '删除账号'),
        (12, 5, 3, '角色列表', '', '', '', 1, '/api/v1/sys/role/list', 'GET', 1, 1, '获取角色列表'),
        (13, 5, 3, '角色详情', '', '', '', 2, '/api/v1/sys/role/detail', 'GET', 1, 1, '获取角色详情'),
        (14, 5, 3, '创建角色', '', '', '', 3, '/api/v1/sys/role/create', 'POST', 1, 1, '创建角色'),
        (15, 5, 3, '更新角色', '', '', '', 4, '/api/v1/sys/role/update', 'PUT', 1, 1, '更新角色'),
        (16, 5, 3, '删除角色', '', '', '', 5, '/api/v1/sys/role/delete', 'DELETE', 1, 1, '删除角色'),
        (17, 5, 3, '所有角色', '', '', '', 6, '/api/v1/sys/role/all', 'GET', 1, 1, '获取所有角色列表'),
        (18, 5, 3, '关联菜单', '', '', '', 7, '/api/v1/sys/role/associate-menus', 'POST', 1, 1, '关联角色和菜单'),
        (19, 6, 3, '菜单列表', '', '', '', 1, '/api/v1/sys/menu/list', 'GET', 1, 1, '获取菜单列表'),
        (20, 6, 3, '所有菜单', '', '', '', 2, '/api/v1/sys/menu/all', 'GET', 1, 1, '获取所有菜单列表'),
        (21, 6, 3, '菜单详情', '', '', '', 3, '/api/v1/sys/menu/detail', 'GET', 1, 1, '获取菜单详情'),
        (22, 6, 3, '创建菜单', '', '', '', 4, '/api/v1/sys/menu/create', 'POST', 1, 1, '创建菜单'),
        (23, 6, 3, '更新菜单', '', '', '', 5, '/api/v1/sys/menu/update', 'PUT', 1, 1, '更新菜单'),
        (24, 6, 3, '删除菜单', '', '', '', 6, '/api/v1/sys/menu/delete', 'DELETE', 1, 1, '删除菜单')
    """)

    # 3. 管理员账号
    op.execute(f"""
        INSERT INTO sys_accounts (id, name, email, password, status)
        VALUES (1, '超级管理员', 'admin@example.com', '{password_hash}', 1)
    """)

    # 4. 角色-菜单关联（所有菜单分配给超级管理员角色）
    op.execute("""
        INSERT INTO sys_role_menus (role_id, menu_id)
        VALUES
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
        (1, 7), (1, 8), (1, 9), (1, 10), (1, 11),
        (1, 12), (1, 13), (1, 14), (1, 15), (1, 16), (1, 17), (1, 18),
        (1, 19), (1, 20), (1, 21), (1, 22), (1, 23), (1, 24)
    """)

    # 5. 账号-角色关联
    op.execute("""
        INSERT INTO sys_account_roles (account_id, role_id)
        VALUES (1, 1)
    """)


def downgrade() -> None:
    """删除初始数据"""
    op.execute("DELETE FROM sys_account_roles")
    op.execute("DELETE FROM sys_role_menus")
    op.execute("DELETE FROM sys_menus WHERE id >= 1")
    op.execute("DELETE FROM sys_accounts WHERE id = 1")
    op.execute("DELETE FROM sys_roles WHERE id = 1")
