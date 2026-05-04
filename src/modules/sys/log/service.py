from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sys_log import SysLog
from src.modules.sys.log.schemas import (LogCreate, LogItem, LogListRequest,
                                         LogListResponse)


class LogService:
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log_data: LogCreate) -> SysLog:
        log = SysLog(**log_data.model_dump())
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_list(self, request: LogListRequest) -> LogListResponse:
        """获取日志列表"""
        stmt = select(SysLog)
        if request.id:
            stmt = stmt.where(SysLog.id == request.id)
        if request.request_ip:
            stmt = stmt.where(SysLog.request_ip.like(f"%{request.request_ip}%"))
        if request.account_id:
            stmt = stmt.where(SysLog.account_id == request.account_id)
        if request.request_method:
            stmt = stmt.where(SysLog.request_method == request.request_method)
        if request.request_path:
            stmt = stmt.where(SysLog.request_path.like(f"%{request.request_path}%"))

        # 统计总数
        count_stmt = select(func.count()).select_from(SysLog)
        if request.id:
            count_stmt = count_stmt.where(SysLog.id == request.id)
        if request.request_ip:
            count_stmt = count_stmt.where(
                SysLog.request_ip.like(f"%{request.request_ip}%")
            )
        if request.account_id:
            count_stmt = count_stmt.where(SysLog.account_id == request.account_id)
        if request.request_method:
            count_stmt = count_stmt.where(
                SysLog.request_method == request.request_method
            )
        if request.request_path:
            count_stmt = count_stmt.where(
                SysLog.request_path.like(f"%{request.request_path}%")
            )
        total = await self.db.scalar(count_stmt) or 0

        # 分页查询
        stmt = stmt.order_by(SysLog.created_time.desc())
        stmt = stmt.offset(request.offset).limit(request.size)
        result = await self.db.execute(stmt)
        logs = list(result.scalars().all())

        # 转换为响应模型
        log_list = [LogItem.model_validate(log) for log in logs]

        return LogListResponse(
            data=log_list,
            total=total,
            page=request.page,
            size=request.size,
        )
