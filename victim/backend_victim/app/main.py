# backend_victim/app/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_health, routes_system
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug mode from environment
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

app = FastAPI(
    title="Victim Monitoring API",
    description="Monitor victim server health and metrics during DDoS attacks",
    version="1.0.0",
    debug=DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_health.router, prefix="/api", tags=["health"])
app.include_router(routes_system.router, prefix="/api", tags=["system"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "service": "Victim DDoS Monitoring API",
        "version": "1.0.0",
        "endpoints": [
            "/api/health",
            "/api/system"
        ]
    }

@app.get("/health")
async def health_check():
    """Simple health check for the API itself"""
    logger.info("API health check endpoint accessed")
    return {"status": "healthy", "service": "victim-api"}

if DEBUG:
    logger.info("Running in DEBUG mode")
    print("🔧 DEBUG MODE ENABLED - Extra metrics will be logged")
