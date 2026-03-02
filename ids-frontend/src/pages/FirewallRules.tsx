// src/pages/FirewallRules.tsx
import { useState, useCallback } from "react";
import { api } from "../api/api";
import type { FirewallRulesResponse } from "../types/api";
import { usePolling } from "../hooks/usePolling";

export default function FirewallRules() {
  const [data, setData] = useState<FirewallRulesResponse | null>(null);

  const fetchData = useCallback(() => {
    api.get("/firewall/rules")
      .then(res => setData(res.data))
      .catch(() => {});
  }, []);

  usePolling(fetchData, 3000);

  if (!data) return <div className="loading">Loading firewall rules</div>;

  return (
    <>
      <div className="section-title">Firewall Rules</div>

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          <span className="badge badge-cyan">Total Rules: {data.total_rules}</span>
          <span className="badge badge-danger">Total Dropped: {data.total_packets.toLocaleString()} packets</span>
        </div>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Target</th>
                <th>Protocol</th>
                <th>Packets</th>
                <th>Bytes</th>
                <th>Rule</th>
              </tr>
            </thead>
            <tbody>
              {data.rules.map((rule) => (
                <tr key={rule.line}>
                  <td>{rule.line}</td>
                  <td>
                    <span className={`badge ${
                      rule.target === 'DROP' ? 'badge-danger' : 
                      rule.target === 'ACCEPT' ? 'badge-success' : 'badge-warning'
                    }`}>
                      {rule.target}
                    </span>
                  </td>
                  <td>{rule.protocol}</td>
                  <td>{rule.pkts.toLocaleString()}</td>
                  <td>{(rule.bytes / 1024).toFixed(2)} KB</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{rule.rule}</td>
                </tr>
              ))}
            </tbody>
          </table>
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
