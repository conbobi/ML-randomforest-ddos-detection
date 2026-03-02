# backend_victim/run.py
# Simple script to run the server

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print("=" * 50)
    print("🚀 Starting Victim Monitoring API")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,  # Different from IDS backend port
        reload=debug,
        log_level="info"
    )
