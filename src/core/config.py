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

    
settings = Settings()
