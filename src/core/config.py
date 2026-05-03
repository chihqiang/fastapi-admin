from __future__ import annotations

import os
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )
    PROJECT_NAME: str = "FastAPI Admin"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = (
        f"sqlite+aiosqlite:///{os.path.join(ROOT_PATH, 'storage', 'fastapi.db')}"
    )
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


settings = Settings()
