import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.exception import register_exception
from src.core.logger import setup_logging
from src.modules.auth import router as auth_router
from src.modules.sys import route as sys_router
from src.schemas.response import success

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting up...")
    yield
    # Shutdown logic
    logger.info("Shutting down...")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}", tags=["auth"])
app.include_router(sys_router.router, prefix=f"{settings.API_V1_STR}")

# 允许所有来源的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
register_exception(app)


@app.get("/health")
async def health_check():
    return success(msg="ok")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
