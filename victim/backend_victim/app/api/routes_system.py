# backend_victim/app/api/routes_system.py

import logging
from fastapi import APIRouter
from app.services.metrics_service import MetricsService
from app.schemas.health_schema import SystemMetricsResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/system", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get system metrics including CPU, memory, network, and active connections
    """
    logger.info("System metrics endpoint called")
    
    metrics = await MetricsService.get_system_metrics()
    
    logger.info(f"System metrics collected - CPU: {metrics['cpu_percent']:.1f}%, "
                f"Memory: {metrics['memory_percent']:.1f}%, "
                f"Active Connections: {metrics['active_connections']}")
    
    print(f"📊 System Metrics - CPU: {metrics['cpu_percent']:.1f}%, "
          f"Memory: {metrics['memory_used_gb']:.2f}GB/{metrics['memory_total_gb']:.2f}GB, "
          f"Network Recv: {metrics['network_bytes_recv'] / 1024 / 1024:.2f}MB")
    
    return metrics
