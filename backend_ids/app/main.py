# backend_ids/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_detection, routes_firewall, routes_system, routes_logs
from app.core.config import settings

app = FastAPI(
    title="IDS Dashboard API",
    description="Real-time DDoS detection and mitigation monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_detection.router, prefix="/api/detection", tags=["detection"])
app.include_router(routes_firewall.router, prefix="/api/firewall", tags=["firewall"])
app.include_router(routes_system.router, prefix="/api/system", tags=["system"])
app.include_router(routes_logs.router, prefix="/api/logs", tags=["logs"])

@app.get("/")
async def root():
    return {
        "service": "IDS Dashboard API",
        "version": "1.0.0",
        "endpoints": [
            "/api/detection/state",
            "/api/firewall/rules",
            "/api/system",
            "/api/logs",
            "/api/top-sources"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
