# backend_ids/app/api/routes_detection.py

from fastapi import APIRouter, HTTPException, status
from app.services.detection_service import DetectionService
from app.schemas.detection_schema import DetectionState, TopSourcesResponse

router = APIRouter()

@router.get("/state", response_model=DetectionState)
async def get_detection_state():
    """
    Get current detection state from live_state.json
    Returns 404 if no detection data available
    """
    state = DetectionService.get_current_state()
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No detection data available. Ensure 06_detect_live.py is running."
        )
    return state

@router.get("/top-sources", response_model=TopSourcesResponse)
async def get_top_sources(limit: int = 10):
    """
    Get top source IPs by connection count from conn.log
    """
    top_sources = DetectionService.get_top_sources(limit)
    return TopSourcesResponse(sources=top_sources)
