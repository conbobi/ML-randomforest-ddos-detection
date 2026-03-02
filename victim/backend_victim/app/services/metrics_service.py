# backend_victim/app/services/metrics_service.py

import logging
import psutil
import time
from typing import Dict
import os

logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

class MetricsService:
    
    @classmethod
    async def get_system_metrics(cls) -> Dict:
        """
        Get system metrics using psutil
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            memory = psutil.virtual_memory()
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)
            
            # Network
            net_io = psutil.net_io_counters()
            
            # Active connections (TCP connections to port 80)
            active_connections = 0
            try:
                connections = psutil.net_connections()
                # Count ESTABLISHED connections to port 80
                active_connections = len([
                    conn for conn in connections 
                    if conn.status == 'ESTABLISHED' and 
                    conn.laddr and conn.laddr.port == 80
                ])
            except (psutil.AccessDenied, psutil.Error) as e:
                logger.warning(f"Cannot access network connections: {str(e)}")
                # Try alternative method - count from /proc
                try:
                    with open('/proc/net/tcp', 'r') as f:
                        lines = f.readlines()[1:]  # Skip header
                        active_connections = len([
                            line for line in lines 
                            if '01' in line.split()[3]  # 01 = ESTABLISHED
                        ])
                except:
                    active_connections = 0
            
            metrics = {
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory.percent, 2),
                'memory_used_gb': round(memory_used_gb, 2),
                'memory_total_gb': round(memory_total_gb, 2),
                'active_connections': active_connections,
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
                'network_packets_sent': net_io.packets_sent,
                'network_packets_recv': net_io.packets_recv,
                'timestamp': time.time()
            }
            
            # Debug prints
            if DEBUG:
                print(f"🔧 DEBUG - CPU: {cpu_percent:.1f}%")
                print(f"🔧 DEBUG - Memory: {memory.percent:.1f}% ({memory_used_gb:.2f}GB/{memory_total_gb:.2f}GB)")
                print(f"🔧 DEBUG - Active Connections: {active_connections}")
                print(f"🔧 DEBUG - Network Sent: {net_io.bytes_sent / 1024 / 1024:.2f}MB")
                print(f"🔧 DEBUG - Network Recv: {net_io.bytes_recv / 1024 / 1024:.2f}MB")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            # Return minimal metrics on error
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'memory_used_gb': 0.0,
                'memory_total_gb': 0.0,
                'active_connections': 0,
                'network_bytes_sent': 0,
                'network_bytes_recv': 0,
                'network_packets_sent': 0,
                'network_packets_recv': 0,
                'timestamp': time.time()
            }
    
    @classmethod
    async def get_connection_stats(cls) -> Dict:
        """
        Get detailed connection statistics
        """
        try:
            connections = psutil.net_connections()
            
            # Group by state
            states = {}
            for conn in connections:
                if conn.laddr and conn.laddr.port == 80:  # Only web connections
                    states[conn.status] = states.get(conn.status, 0) + 1
            
            if DEBUG:
                print(f"🔧 DEBUG - Connection states: {states}")
            
            return {
                'total': len(connections),
                'by_state': states,
                'web_connections': sum(1 for conn in connections 
                                     if conn.laddr and conn.laddr.port == 80)
            }
        except Exception as e:
            logger.error(f"Error getting connection stats: {str(e)}")
            return {'total': 0, 'by_state': {}, 'web_connections': 0}
