# backend_victim/app/api/routes_health.py

import logging
from fastapi import APIRouter, HTTPException
from app.services.nginx_service import NginxService
from app.schemas.health_schema import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse)
async def get_health_status():
    """
    Check if nginx is responding on localhost:80
    Returns health status, HTTP code, and response time
    """
    logger.info("Health check endpoint called")
    
    result = await NginxService.check_health()
    
    if result is None:
        logger.error("Failed to check nginx health")
        raise HTTPException(status_code=503, detail="Unable to check nginx health")
    
    logger.info(f"Health check completed - Status: {result['status']}, Code: {result['http_code']}")
    print(f"📊 Health Check - Response time: {result['response_time_ms']:.2f}ms")
    
    return result
