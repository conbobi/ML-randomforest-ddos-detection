# backend_ids/app/schemas/detection_schema.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DetectionFeatures(BaseModel):
    total_connections: int
    syn_connections: int
    unique_src_ips: int
    connections_per_second: float
    failed_ratio: float

class DetectionState(BaseModel):
    timestamp: int
    label: int
    confidence: float
    defense_mode: bool
    features: DetectionFeatures
    consecutive_attacks: int
    
    @property
    def is_attack(self) -> bool:
        return self.label == 1
    
    @property
    def time_str(self) -> str:
        return datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")

class TopSource(BaseModel):
    ip: str
    count: int
    percentage: float

class TopSourcesResponse(BaseModel):
    sources: List[TopSource]
    total_connections: Optional[int] = None
