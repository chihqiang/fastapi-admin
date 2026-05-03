"""
FastAPI Admin 应用程序入口

用法:
    python main.py run          # 启动开发服务器
    alembic upgrade head        # 执行数据库迁移
"""

import logging

import uvicorn

from src.boot import create_app
from src.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = create_app()


def run() -> None:
    """启动 FastAPI 开发服务器"""
    logger.info("=" * 50)
    logger.info(f"项目名称: {settings.PROJECT_NAME}")
    logger.info(f"服务器地址: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    logger.info("=" * 50)

    try:
        uvicorn.run(
            app="main:app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            factory=False,
            log_config=None,
        )
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号，正在关闭服务器...")
    finally:
        logger.info("服务器已停止运行")


if __name__ == "__main__":
    run()
