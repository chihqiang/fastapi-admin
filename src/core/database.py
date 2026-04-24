from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    # 数据库连接URL，从配置文件读取
    settings.DATABASE_URL,
    # 是否打印执行的SQL语句，生产环境关闭
    echo=False,
    # 启用SQLAlchemy 2.0 新特性
    future=True,
    # 连接前检查有效性，防止连接失效
    pool_pre_ping=True,
    # 连接5分钟后自动回收，避免数据库超时
    pool_recycle=300,
)

# 创建异步会话工厂，用于生成数据库会话
AsyncSessionLocal = async_sessionmaker(
    # 绑定数据库引擎
    bind=engine,
    # 指定使用异步会话类
    class_=AsyncSession,
    # 提交后不销毁对象，避免数据丢失
    expire_on_commit=False,
    # 关闭自动刷新，提升程序运行性能
    autoflush=False,
)


# ORM模型基类，所有数据表模型都继承此类
class Base(DeclarativeBase):
    pass


# FastAPI依赖项：获取异步数据库会话，自动管理创建与关闭
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            # 提供会话给API请求使用
            yield session
        finally:
            # 请求结束后自动关闭会话
            await session.close()
