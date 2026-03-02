# backend_victim/app/schemas/health_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Literal

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: Literal["HEALTHY", "DOWN"] = Field(..., description="Service health status")
    http_code: int = Field(..., description="HTTP status code returned", ge=0, le=599)
    response_time_ms: float = Field(..., description="Response time in milliseconds", ge=0)

class SystemMetricsResponse(BaseModel):
    """System metrics response schema"""
    cpu_percent: float = Field(..., description="CPU usage percentage", ge=0, le=100)
    memory_percent: float = Field(..., description="Memory usage percentage", ge=0, le=100)
    memory_used_gb: float = Field(..., description="Memory used in GB", ge=0)
    memory_total_gb: float = Field(..., description="Total memory in GB", ge=0)
    active_connections: int = Field(..., description="Number of active connections to port 80", ge=0)
    network_bytes_sent: int = Field(..., description="Total bytes sent", ge=0)
    network_bytes_recv: int = Field(..., description="Total bytes received", ge=0)
    network_packets_sent: int = Field(..., description="Total packets sent", ge=0)
    network_packets_recv: int = Field(..., description="Total packets received", ge=0)
    timestamp: float = Field(..., description="Unix timestamp of metrics collection")

class NginxMetricsResponse(BaseModel):
    """Nginx metrics response schema"""
    rps: float = Field(..., description="Requests per second", ge=0)
    p95_latency_ms: float = Field(..., description="P95 latency in milliseconds", ge=0)
    active_connections: int = Field(..., description="Active connections to nginx", ge=0)
