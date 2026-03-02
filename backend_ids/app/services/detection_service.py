# backend_ids/app/services/detection_service.py

import json
import os
from typing import Optional, List, Dict, Any
from collections import Counter
from app.core.config import settings
from app.schemas.detection_schema import DetectionState, DetectionFeatures, TopSource

class DetectionService:
    
    @staticmethod
    def get_current_state() -> Optional[DetectionState]:
        """
        Read live_state.json and parse into DetectionState
        """
        try:
            if not os.path.exists(settings.live_state_path):
                return None
            
            with open(settings.live_state_path, 'r') as f:
                data = json.load(f)
            
            # Validate required fields
            required = ['timestamp', 'label', 'confidence', 'defense_mode', 'features', 'consecutive_attacks']
            if not all(k in data for k in required):
                return None
            
            # Parse features
            features = DetectionFeatures(**data['features'])
            
            return DetectionState(
                timestamp=data['timestamp'],
                label=data['label'],
                confidence=data['confidence'],
                defense_mode=data['defense_mode'],
                features=features,
                consecutive_attacks=data['consecutive_attacks']
            )
        except (json.JSONDecodeError, KeyError, TypeError, FileNotFoundError):
            return None
    
    @staticmethod
    def get_defense_logs(lines: int = 20) -> Optional[List[str]]:
        """
        Read last N lines from defense_mode.log
        """
        try:
            if not os.path.exists(settings.defense_log_path):
                return None
            
            with open(settings.defense_log_path, 'r') as f:
                all_lines = f.readlines()
            
            # Get last N lines, strip newlines
            last_lines = [line.strip() for line in all_lines[-lines:] if line.strip()]
            return last_lines
        except (IOError, OSError):
            return None
    
    @staticmethod
    def get_top_sources(limit: int = 10) -> List[TopSource]:
        """
        Parse conn.log and get top source IPs by connection count
        """
        try:
            if not os.path.exists(settings.conn_log_path):
                return []
            
            src_ips = []
            total = 0
            
            with open(settings.conn_log_path, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) > 2:
                        src_ip = parts[2]  # id.orig_h
                        if src_ip and src_ip != '-':
                            src_ips.append(src_ip)
                            total += 1
            
            if not src_ips:
                return []
            
            # Count and get top N
            counter = Counter(src_ips)
            top = counter.most_common(limit)
            
            return [
                TopSource(
                    ip=ip,
                    count=count,
                    percentage=(count / total) * 100 if total > 0 else 0
                )
                for ip, count in top
            ]
        except (IOError, OSError, IndexError):
            return []
