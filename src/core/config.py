from __future__ import annotations

import os
from typing import ClassVar, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )
    PROJECT_NAME: str = "FastAPI Admin"
    API_V1_STR: str = "/api/v1"
    
    # ================================================= #
    # ******************* 登录认证配置 ****************** #
    # ================================================= #
    SECRET_KEY: str = "9d33c5e5c93ffed4bbf296f902253535b2058adc9322fb810545473b3e2b5366"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ================================================= #
    # ******************* 服务器配置 ****************** #
    # ================================================= #
    SERVER_HOST: str = "0.0.0.0"  # 允许访问的IP地址
    SERVER_PORT: int = 8000  # 服务端口

    # ================================================= #
    # ******************** 跨域配置 ******************** #
    # ================================================= #
    CORS_ORIGIN_ENABLE: bool = True  # 是否启用跨域
    ALLOW_ORIGINS: list[str] = ["*"]  # 允许的域名列表
    ALLOW_METHODS: list[str] = ["*"]  # 允许的HTTP方法
    ALLOW_HEADERS: list[str] = ["*"]  # 允许的请求头
    ALLOW_CREDENTIALS: bool = True  # 是否允许携带cookie
    CORS_EXPOSE_HEADERS: list[str] = ["X-Request-ID"]
    # ================================================= #
    # ******************** 数据库配置 ******************* #
    # ================================================= #
    DATABASE_URL: str = (
        f"sqlite+aiosqlite:///{os.path.join(ROOT_PATH, 'storage', 'fastapi.db')}"
    )
    DATABASE_ECHO: bool | Literal["debug"] = False  # 是否显示SQL日志
    ECHO_POOL: bool | Literal["debug"] = False  # 是否显示连接池日志
    POOL_SIZE: int = 10  # 连接池大小
    MAX_OVERFLOW: int = 20  # 最大溢出连接数
    POOL_TIMEOUT: int = 30  # 连接超时时间(秒)
    POOL_RECYCLE: int = 1800  # 连接回收时间(秒)
    POOL_USE_LIFO: bool = True  # 是否使用LIFO连接池
    POOL_PRE_PING: bool = True  # 是否开启连接预检
    FUTURE: bool = True  # 是否使用SQLAlchemy 2.0特性
    AUTOCOMMIT: bool = False  # 是否自动提交
    AUTOFETCH: bool = False  # 是否自动刷新
    EXPIRE_ON_COMMIT: bool = False  # 是否在提交时过期
    # ================================================= #
    # ******************* Gzip压缩配置 ******************* #
    # ================================================= #
    GZIP_ENABLE: bool = True  # 是否启用Gzip
    GZIP_MIN_SIZE: int = 1000  # 最小压缩大小(字节)
    GZIP_COMPRESS_LEVEL: int = 9  # 压缩级别(1-9)

settings = Settings()
