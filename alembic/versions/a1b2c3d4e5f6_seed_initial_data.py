"""seed initial data from json (universal version)

Revision ID: a1b2c3d4e5f6
Revises: c6c4b787c863
Create Date: 2026-05-03 15:05:00.000000

"""

import json
import os
from typing import Sequence, Union

import bcrypt
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "c6c4b787c863"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ====================== 核心配置 ======================
# JSON key => 数据库表名
TABLE_MAP = {
    "accounts": "sys_accounts",
    "roles": "sys_roles",
    "menus": "sys_menus",
}

# 多对多关联表配置 (表名, 左ID, 右ID)
MANY_TO_MANY = [
    ("sys_account_roles", "account_id", "role_id"),
    ("sys_role_menus", "role_id", "menu_id"),
]

# 需要加密的密码字段
PASSWORD_FIELDS = ["password"]

# 插入时自动填充的默认值
DEFAULT_FIELDS = {
    "sys_accounts": {"status": 1},  # 1 = 启用
}
# ======================================================


def load_json() -> dict:
    """加载初始 JSON 数据"""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sql_escape(val):
    """安全转义 SQL 值"""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).replace("'", "''")
    return f"'{s}'"


def build_insert_sql(table: str, data: dict) -> str:
    """自动构建插入 SQL（支持任意字段）"""
    cols = []
    vals = []
    for k, v in data.items():
        cols.append(k)
        vals.append(sql_escape(v))
    cols_str = ",".join(cols)
    vals_str = ",".join(vals)
    return f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str})"


# ====================== 升级：插入数据 ======================
def upgrade() -> None:
    data = load_json()

    # 1. 插入普通表
    for json_key, table in TABLE_MAP.items():
        for item in data.get(json_key, []):
            # 自动填充默认值
            if table in DEFAULT_FIELDS:
                item.update(DEFAULT_FIELDS[table])
            # 自动加密密码
            for field in PASSWORD_FIELDS:
                if field in item:
                    raw_pwd = item[field]
                    item[field] = bcrypt.hashpw(
                        raw_pwd.encode(), bcrypt.gensalt()
                    ).decode()
            sql = build_insert_sql(table, item)
            op.execute(text(sql))

    # 2. 插入多对多关联
    for rel_table, id_left, id_right in MANY_TO_MANY:
        for item in data.get(rel_table, []):
            left_val = item[id_left]
            right_vals = item[f"{id_right}s"]  # menu_ids / role_ids
            for rv in right_vals:
                op.execute(
                    text(
                        f"INSERT INTO {rel_table} ({id_left}, {id_right}) VALUES ({left_val}, {rv})"
                    )
                )


# ====================== 降级：只删除 JSON 里的数据 ======================
def downgrade() -> None:
    data = load_json()

    # 1. 删除多对多关联表（按 JSON 里的 ID 删除）
    for rel_table, id_left, id_right in MANY_TO_MANY:
        for item in data.get(rel_table, []):
            left_val = item[id_left]
            right_vals = item[f"{id_right}s"]
            for rv in right_vals:
                op.execute(
                    text(
                        f"DELETE FROM {rel_table} WHERE {id_left} = {left_val} AND {id_right} = {rv}"
                    )
                )

    # 2. 删除主表（只删除 JSON 里的 id）
    for json_key, table in TABLE_MAP.items():
        ids = [str(item["id"]) for item in data.get(json_key, []) if "id" in item]
        if ids:
            id_str = ",".join(ids)
            op.execute(text(f"DELETE FROM {table} WHERE id IN ({id_str})"))
