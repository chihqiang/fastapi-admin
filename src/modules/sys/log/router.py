from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthPermission
from src.models import Account
from src.modules.sys.log.schemas import LogListRequest, LogListResponse
from src.modules.sys.log.service import LogService
from src.schemas.response import ResponseSchema, success

router = APIRouter(prefix="/log", tags=["系统管理-日志管理"])


@router.get("/list", response_model=ResponseSchema[LogListResponse])
async def log_list(
    request: Annotated[LogListRequest, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        Account, Depends(AuthPermission(api_url="/sys/log/list", api_method="GET"))
    ],
):
    """获取账号列表"""
    service = LogService(db)
    result = await service.get_list(request)
    return success(data=result)
