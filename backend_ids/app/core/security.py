# backend_ids/app/core/security.py

import subprocess
from typing import List, Optional

def run_iptables_command(args: List[str]) -> Optional[str]:
    """
    Run iptables command safely without shell=True
    """
    try:
        cmd = ["sudo", "iptables"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None
