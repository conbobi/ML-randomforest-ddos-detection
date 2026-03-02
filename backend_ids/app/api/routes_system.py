# backend_ids/app/api/routes_system.py

from fastapi import APIRouter
from app.services.metrics_service import MetricsService
from pydantic import BaseModel

router = APIRouter()

class SystemMetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int
    timestamp: float

@router.get("/", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get system metrics (CPU, memory, network)
    """
    return MetricsService.get_system_metrics()
