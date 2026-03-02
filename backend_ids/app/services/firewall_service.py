# backend_ids/app/services/firewall_service.py

import re
from typing import List, Optional
from app.core.security import run_iptables_command
from app.schemas.firewall_schema import FirewallRule
from app.core.config import settings
class FirewallService:
    
    # Regex pattern for iptables -L FORWARD -v -n --line-numbers
    # Example: 
    # 1   1234 56789 DROP    tcp  --  *      *       0.0.0.0/0    0.0.0.0/0    tcp dpt:80
    IPTABLES_PATTERN = re.compile(
        r'^\s*(?P<line>\d+)\s+'           # line number
        r'(?P<pkts>\d+)\s+'                # packets
        r'(?P<bytes>\d+)\s+'                # bytes
        r'(?P<target>\w+)\s+'               # target (DROP, ACCEPT)
        r'(?P<prot>\w+)\s+'                  # protocol
        r'(?P<opt>\S+)\s+'                    # options
        r'(?P<in>\S+)\s+'                      # input interface
        r'(?P<out>\S+)\s+'                     # output interface
        r'(?P<source>[\d\./]+)\s+'              # source
        r'(?P<destination>[\d\./]+)\s*'         # destination
        r'(?P<extra>.*)$'                         # extra options
    )
    
    @classmethod
    def get_forward_rules(cls) -> Optional[List[FirewallRule]]:
        """
        Get FORWARD chain rules with counters using iptables -L -v -n --line-numbers
        """
        output = run_iptables_command([
            '-L', settings.IPTABLES_CHAIN,
            '-v', '-n', '--line-numbers'
        ])
        
        if output is None:
            return None
        
        rules = []
        lines = output.split('\n')
        
        # Skip header lines (usually first 2 lines)
        data_lines = [l for l in lines if l and not l.startswith('Chain') and 'num' not in l]
        
        for line in data_lines:
            rule = cls._parse_iptables_line(line)
            if rule:
                rules.append(rule)
        
        return rules
    
    @classmethod
    def _parse_iptables_line(cls, line: str) -> Optional[FirewallRule]:
        """
        Parse a single iptables line into FirewallRule
        """
        match = cls.IPTABLES_PATTERN.match(line)
        if not match:
            return None
        
        try:
            return FirewallRule(
                line=int(match.group('line')),
                pkts=int(match.group('pkts')),
                bytes=int(match.group('bytes')),
                target=match.group('target'),
                protocol=match.group('prot'),
                rule=line.strip()
            )
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def get_rate_limit_stats() -> Optional[dict]:
        """
        Get statistics about rate limiting rules
        """
        rules = FirewallService.get_forward_rules()
        if not rules:
            return None
        
        rate_limit_rules = [r for r in rules if 'limit' in r.rule]
        drop_rules = [r for r in rules if r.target == 'DROP']
        
        return {
            'total_rules': len(rules),
            'rate_limit_rules': len(rate_limit_rules),
            'drop_rules': len(drop_rules),
            'total_packets_dropped': sum(r.pkts for r in drop_rules),
            'total_bytes_dropped': sum(r.bytes for r in drop_rules)
        }
