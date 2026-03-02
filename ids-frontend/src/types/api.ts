export interface DetectionFeatures {
  total_connections: number;
  syn_connections: number;
  unique_src_ips: number;
  connections_per_second: number;
  failed_ratio: number;
}

export interface DetectionState {
  timestamp: number;
  label: number;
  confidence: number;
  defense_mode: boolean;
  features: DetectionFeatures;
  consecutive_attacks: number;
}

export interface TopSource {
  ip: string;
  count: number;
  percentage: number;
}

export interface FirewallRule {
  line: number;
  pkts: number;
  bytes: number;
  target: string;
  protocol: string;
  rule: string;
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  network_packets_sent: number;
  network_packets_recv: number;
  timestamp: number;
}
