from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.system_service import check_system_resources
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/resources")
async def get_system_resources():
    logger.info("Checking system resources.")
    result = check_system_resources()
    return JSONResponse(content=result.dict())
