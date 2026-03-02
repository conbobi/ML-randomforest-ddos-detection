// src/pages/TopSources.tsx
import { useState, useCallback } from "react";
import { api } from "../api/api";
import type { TopSourcesResponse } from "../types/api";
import { usePolling } from "../hooks/usePolling";

export default function TopSources() {
  const [data, setData] = useState<TopSourcesResponse | null>(null);

  const fetchData = useCallback(() => {
    api.get("/detection/top-sources")
      .then(res => setData(res.data))
      .catch(() => {});
  }, []);

  usePolling(fetchData, 3000);

  if (!data) return <div className="loading">Loading top sources</div>;

  return (
    <>
      <div className="section-title">Top Threat Sources</div>

      <div className="card">
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Source IP</th>
                <th>Connections</th>
                <th>Percentage</th>
                <th>Threat Level</th>
              </tr>
            </thead>
            <tbody>
              {data.sources.map((source, index) => {
                const threatLevel = source.percentage > 50 ? 'high' : source.percentage > 20 ? 'medium' : 'low';
                return (
                  <tr key={index}>
                    <td>#{index + 1}</td>
                    <td>
                      <span className="badge badge-cyan">{source.ip}</span>
                    </td>
                    <td>{source.count.toLocaleString()}</td>
                    <td>{source.percentage.toFixed(2)}%</td>
                    <td>
                      <span className={`badge ${
                        threatLevel === 'high' ? 'badge-danger' : 
                        threatLevel === 'medium' ? 'badge-warning' : 'badge-success'
                      }`}>
                        {threatLevel.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                );
              })}
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
