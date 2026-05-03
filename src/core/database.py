from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    url=settings.ASYNC_DB_URI,
    echo=settings.DATABASE_ECHO,
    echo_pool=settings.ECHO_POOL,
    pool_pre_ping=settings.POOL_PRE_PING,
    future=settings.FUTURE,
    pool_recycle=settings.POOL_RECYCLE,
)
# engine = create_async_engine(
#     url=settings.DATABASE_URL,
#     echo=settings.DATABASE_ECHO,
#     echo_pool=settings.ECHO_POOL,
#     pool_pre_ping=settings.POOL_PRE_PING,
#     future=settings.FUTURE,
#     pool_recycle=settings.POOL_RECYCLE,
#     pool_size=settings.POOL_SIZE,
#     max_overflow=settings.MAX_OVERFLOW,
#     pool_timeout=settings.POOL_TIMEOUT,
#     pool_use_lifo=settings.POOL_USE_LIFO,
# )
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


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
