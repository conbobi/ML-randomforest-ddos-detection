// src/pages/Logs.tsx
import { useState, useCallback } from "react";
import { api } from "../api/api";
import type { LogsResponse } from "../types/api";
import { usePolling } from "../hooks/usePolling";

export default function Logs() {
  const [data, setData] = useState<LogsResponse | null>(null);

  const fetchData = useCallback(() => {
    api.get("/logs")
      .then(res => setData(res.data))
      .catch(() => {});
  }, []);

  usePolling(fetchData, 3000);

  if (!data) return <div className="loading">Loading logs</div>;

  return (
    <>
      <div className="section-title">Security Events</div>

      <div className="card">
        <div style={{ marginBottom: '1rem' }}>
          <span className="badge badge-cyan">Total Lines: {data.total_lines}</span>
        </div>

        <div style={{ 
          background: 'var(--bg-primary)', 
          padding: '1rem', 
          borderRadius: '8px',
          maxHeight: '400px',
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.85rem'
        }}>
          {data.logs.map((log, index) => {
            const isAttack = log.includes('ATTACK') || log.includes('ENABLED');
            const isWarning = log.includes('WARNING');
            const color = isAttack ? 'var(--accent-red)' : isWarning ? 'var(--accent-yellow)' : 'var(--text-secondary)';
            
            return (
              <div 
                key={index}
                style={{ 
                  padding: '0.25rem 0',
                  color,
                  borderBottom: index < data.logs.length - 1 ? '1px solid var(--border)' : 'none'
                }}
              >
                <span style={{ color: 'var(--text-tertiary)' }}>[{index + 1}]</span> {log}
              </div>
            );
          })}
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-header">
          <span className="card-title">Raw Response</span>
        </div>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </>
  );
}
