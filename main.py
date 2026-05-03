"""
FastAPI Admin 应用程序入口

用法:
    python main.py run          # 启动开发服务器
"""

import logging

import typer
import uvicorn

from src import boot
from src.core.config import settings
from src.core.logger import setup_logging

app = boot.create_app()
cli = typer.Typer()
setup_logging()


@cli.command(
    name="run",
    help="启动 FastAPI 开发服务器",
)
def run() -> None:
    """启动 FastAPI 开发服务器"""
    logging.info("=" * 50)
    logging.info(f"项目名称: {settings.PROJECT_NAME}")
    logging.info(f"服务器地址: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    logging.info("=" * 50)

    try:
        uvicorn.run(
            app="main:app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            factory=False,
            log_config=None,
        )
    except KeyboardInterrupt:
        logging.info("收到键盘中断信号，正在关闭服务器...")
    finally:
        logging.info("服务器已停止运行")


if __name__ == "__main__":
    cli()
