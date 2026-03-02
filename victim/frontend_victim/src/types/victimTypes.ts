// frontend_victim/src/types/victimTypes.ts

export type HealthStatus = "HEALTHY" | "DOWN";

export interface HealthResponse {
  status: HealthStatus;
  http_code: number;
  response_time_ms: number;
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  active_connections: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  network_packets_sent: number;
  network_packets_recv: number;
  timestamp: number;
}

export interface ChartDataPoint {
  timestamp: number;
  value: number;
}

export interface NetworkChartDataPoint {
  timestamp: number;
  rx: number;
  tx: number;
}
