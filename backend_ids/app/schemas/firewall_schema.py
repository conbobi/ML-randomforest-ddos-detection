# backend_ids/app/schemas/firewall_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class FirewallRule(BaseModel):
    line: int
    pkts: int
    bytes: int
    target: str
    protocol: str
    rule: str
    
    @property
    def pkts_per_sec_delta(self) -> Optional[int]:
        """Can be used to track rate changes"""
        return None

class FirewallRulesResponse(BaseModel):
    rules: List[FirewallRule]
    total_rules: int = Field(0, alias="total_rules")
    total_packets: int = Field(0, alias="total_packets")
    total_bytes: int = Field(0, alias="total_bytes")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.total_rules = len(self.rules)
        self.total_packets = sum(r.pkts for r in self.rules)
        self.total_bytes = sum(r.bytes for r in self.rules)
