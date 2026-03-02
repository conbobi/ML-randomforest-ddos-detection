# backend_ids/app/api/routes_logs.py

from fastapi import APIRouter, HTTPException, status
from app.services.detection_service import DetectionService
from pydantic import BaseModel
from typing import List

router = APIRouter()

class LogsResponse(BaseModel):
    logs: List[str]
    total_lines: int

@router.get("/", response_model=LogsResponse)
async def get_defense_logs(lines: int = 20):
    """
    Get last N lines from defense_mode.log
    """
    logs = DetectionService.get_defense_logs(lines)
    if logs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="defense_mode.log not found"
        )
    return LogsResponse(logs=logs, total_lines=len(logs))
