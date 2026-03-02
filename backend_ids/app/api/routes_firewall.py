# backend_ids/app/api/routes_firewall.py

from fastapi import APIRouter, HTTPException, status
from app.services.firewall_service import FirewallService
from app.schemas.firewall_schema import FirewallRulesResponse, FirewallRule

router = APIRouter()

@router.get("/rules", response_model=FirewallRulesResponse)
async def get_firewall_rules():
    """
    Get current iptables FORWARD chain rules with packet/byte counters
    """
    rules = FirewallService.get_forward_rules()
    if rules is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to retrieve iptables rules. Check permissions."
        )
    return FirewallRulesResponse(rules=rules)
