# backend_victim/app/services/nginx_service.py

import logging
import time
import asyncio
import aiohttp
from typing import Optional, Dict, List
from collections import deque
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class NginxService:
    _rps_history = deque(maxlen=100)  # Store last 100 timestamps for RPS calculation
    
    @classmethod
    async def check_health(cls) -> Optional[Dict]:
        """
        Check if nginx is responding on localhost:80
        Returns health status, HTTP code, and response time
        """
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:80", timeout=5.0) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Record this request for RPS calculation
                    cls._rps_history.append(time.time())
                    
                    logger.info(f"Nginx health check - Status: {response.status}, Time: {response_time:.2f}ms")
                    
                    # Debug print
                    print(f"🔍 Nginx Check - HTTP {response.status}, Response time: {response_time:.2f}ms")
                    
                    return {
                        "status": "HEALTHY" if response.status == 200 else "DOWN",
                        "http_code": response.status,
                        "response_time_ms": round(response_time, 2)
                    }
                    
        except aiohttp.ClientConnectorError:
            logger.error("Nginx is not running or not accessible on localhost:80")
            print("❌ Nginx connection failed - Service may be down")
            return {
                "status": "DOWN",
                "http_code": 0,
                "response_time_ms": 0.0
            }
        except asyncio.TimeoutError:
            logger.error("Nginx health check timed out after 5 seconds")
            print("⏱️ Nginx health check timed out")
            return {
                "status": "DOWN",
                "http_code": 0,
                "response_time_ms": 0.0
            }
        except Exception as e:
            logger.error(f"Unexpected error checking nginx health: {str(e)}")
            print(f"❌ Unexpected error: {str(e)}")
            return None
    
    @classmethod
    async def get_rps(cls, window_seconds: int = 10) -> float:
        """
        Calculate requests per second from nginx access.log
        Uses last window_seconds of requests
        """
        try:
            access_log_path = "/var/log/nginx/access.log"
            
            if not os.path.exists(access_log_path):
                logger.warning(f"Access log not found: {access_log_path}")
                return 0.0
            
            # Get current time
            now = datetime.now()
            cutoff_time = now - timedelta(seconds=window_seconds)
            
            # Read last 1000 lines or so for performance
            lines = []
            with open(access_log_path, 'r') as f:
                # Go to end of file and read backwards
                f.seek(0, 2)
                file_size = f.tell()
                block_size = 4096
                
                # Read from the end
                data = []
                bytes_read = 0
                while bytes_read < file_size and len(data) < 1000:  # Limit to 1000 lines
                    block_size = min(block_size, file_size - bytes_read)
                    f.seek(file_size - bytes_read - block_size)
                    block = f.read(block_size)
                    data.insert(0, block)
                    bytes_read += block_size
                    lines = ''.join(data).splitlines()
            
            if not lines:
                return 0.0
            
            # Count requests in the last window_seconds
            # This is simplified - real implementation would parse timestamps
            # For now, use the history we stored from health checks
            current_time = time.time()
            recent_requests = [t for t in cls._rps_history if current_time - t <= window_seconds]
            
            rps = len(recent_requests) / window_seconds
            
            if DEBUG and os.getenv("DEBUG") == "True":
                print(f"📈 RPS (last {window_seconds}s): {rps:.2f}")
            
            return round(rps, 2)
            
        except Exception as e:
            logger.error(f"Error calculating RPS: {str(e)}")
            return 0.0
    
    @classmethod
    async def get_p95_latency(cls) -> float:
        """
        Calculate P95 latency from nginx access.log
        """
        # Simplified implementation
        # In production, parse actual latency from access log
        # For demo, return mock value based on health checks
        try:
            # This would parse actual latency values from log
            # For now, return a reasonable value
            return 25.5  # ms
        except Exception as e:
            logger.error(f"Error calculating P95 latency: {str(e)}")
            return 0.0
