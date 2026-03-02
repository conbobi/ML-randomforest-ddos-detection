# backend_ids/app/services/metrics_service.py

import psutil
import time
from typing import Dict, Any

class MetricsService:
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Get system metrics using psutil
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        
        # Network
        net_io = psutil.net_io_counters()
        
        return {
            'cpu_percent': round(cpu_percent, 2),
            'memory_percent': round(memory.percent, 2),
            'memory_used_gb': round(memory_used_gb, 2),
            'memory_total_gb': round(memory_total_gb, 2),
            'network_bytes_sent': net_io.bytes_sent,
            'network_bytes_recv': net_io.bytes_recv,
            'network_packets_sent': net_io.packets_sent,
            'network_packets_recv': net_io.packets_recv,
            'timestamp': time.time()
        }
    
    @staticmethod
    def get_network_stats() -> Dict[str, Any]:
        """
        Get detailed network statistics
        """
        net_io = psutil.net_io_counters()
        net_connections = psutil.net_connections()
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'err_in': net_io.errin,
            'err_out': net_io.errout,
            'drop_in': net_io.dropin,
            'drop_out': net_io.dropout,
            'active_connections': len(net_connections)
        }
