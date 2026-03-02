// src/pages/SystemMetrics.tsx
import { useState, useCallback } from "react";
import { api } from "../api/api";
import type { SystemMetrics } from "../types/api";
import { usePolling } from "../hooks/usePolling";

export default function SystemMetricsPage() {
  const [data, setData] = useState<SystemMetrics | null>(null);

  const fetchData = useCallback(() => {
    api.get("/system")
      .then(res => setData(res.data))
      .catch(() => {});
  }, []);

  usePolling(fetchData, 2000);

  if (!data) return <div className="loading">Loading system metrics</div>;

  return (
    <>
      <div className="section-title">System Metrics</div>

      <div className="grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">CPU Usage</span>
          </div>
          <div className="card-value">{data.cpu_percent}%</div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${data.cpu_percent > 80 ? 'critical' : data.cpu_percent > 50 ? 'warning' : 'normal'}`}
              style={{ width: `${data.cpu_percent}%` }}
            />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Memory Usage</span>
          </div>
          <div className="card-value">{data.memory_percent}%</div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${data.memory_percent > 80 ? 'critical' : data.memory_percent > 50 ? 'warning' : 'normal'}`}
              style={{ width: `${data.memory_percent}%` }}
            />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Memory Used</span>
          </div>
          <div className="card-value">
            {data.memory_used_gb.toFixed(2)} <span className="card-unit">GB</span>
          </div>
          <div className="card-title">
            Total: {data.memory_total_gb.toFixed(2)} GB
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Network I/O</span>
          </div>
          <div style={{ marginBottom: '0.5rem' }}>
            <span className="card-title">TX: </span>
            <span className="card-value small">
              {(data.network_bytes_sent / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
          <div>
            <span className="card-title">RX: </span>
            <span className="card-value small">
              {(data.network_bytes_recv / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">Packets Sent</span>
          <span className="stat-value">{data.network_packets_sent.toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Packets Received</span>
          <span className="stat-value">{data.network_packets_recv.toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Timestamp</span>
          <span className="stat-value">{new Date(data.timestamp * 1000).toLocaleTimeString()}</span>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">Raw Response</span>
        </div>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </>
  );
}
