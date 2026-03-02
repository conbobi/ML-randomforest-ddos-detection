// src/pages/DetectionState.tsx
import { useState, useCallback } from "react";
import { api } from "../api/api";
import type { DetectionState } from "../types/api";
import { usePolling } from "../hooks/usePolling";

export default function DetectionStatePage() {
  const [data, setData] = useState<DetectionState | null>(null);

  const fetchData = useCallback(() => {
    api.get("/detection/state")
      .then(res => setData(res.data))
      .catch(() => {});
  }, []);

  usePolling(fetchData, 2000);

  if (!data) return <div className="loading">Loading detection data</div>;

  const isAttack = data.label === 1;
  const confidencePercent = (data.confidence * 100).toFixed(1);

  return (
    <>
      {isAttack && (
        <div className="attack-banner">
          <div className="attack-banner-left">
            <span className="attack-icon">🚨</span>
            <div>
              <div className="attack-title">DDoS ATTACK DETECTED</div>
              <div style={{ color: 'rgba(255,255,255,0.8)' }}>
                Confidence: {confidencePercent}% • {data.features.connections_per_second} conn/s
              </div>
            </div>
          </div>
          <span className="attack-badge">ACTIVE</span>
        </div>
      )}

      <div className={`card ${isAttack ? 'attack' : ''}`} style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <span className="card-title">System Status</span>
          <span>{isAttack ? '⚠️' : '✅'}</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <span className={`badge ${isAttack ? 'badge-danger' : 'badge-success'}`}>
            {isAttack ? 'DDoS ATTACK' : 'NORMAL'}
          </span>
          <span className="card-title">
            Consecutive attacks: <strong>{data.consecutive_attacks}</strong>
          </span>
        </div>
      </div>

      <div className="grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Confidence</span>
          </div>
          <div className="card-value">{confidencePercent}%</div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${data.confidence > 0.7 ? 'critical' : data.confidence > 0.4 ? 'warning' : 'normal'}`}
              style={{ width: `${confidencePercent}%` }}
            />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Connections/sec</span>
          </div>
          <div className="card-value">{data.features.connections_per_second}</div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${data.features.connections_per_second > 1000 ? 'critical' : data.features.connections_per_second > 500 ? 'warning' : 'normal'}`}
              style={{ width: `${Math.min((data.features.connections_per_second / 2000) * 100, 100)}%` }}
            />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Unique Sources</span>
          </div>
          <div className="card-value">{data.features.unique_src_ips}</div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Defense Mode</span>
          </div>
          <div className="card-value">{data.defense_mode ? 'ACTIVE' : 'OFF'}</div>
          {data.defense_mode && (
            <div className="badge badge-danger" style={{ marginTop: '0.5rem' }}>
              PROTECTING
            </div>
          )}
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">Total Connections</span>
          <span className="stat-value">{data.features.total_connections}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">SYN Connections</span>
          <span className="stat-value">{data.features.syn_connections}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Failed Ratio</span>
          <span className="stat-value">{(data.features.failed_ratio * 100).toFixed(1)}%</span>
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
