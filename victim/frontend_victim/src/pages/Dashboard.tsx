// frontend_victim/src/pages/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import { victimApi } from '../api/victimApi';
import { usePolling } from '../hooks/usePolling';
import { HealthResponse, SystemMetrics, ChartDataPoint, NetworkChartDataPoint } from '../types/victimTypes';

import StatusCard from '../components/kpi/StatusCard';
import RPSCard from '../components/kpi/RPSCard';
import LatencyCard from '../components/kpi/LatencyCard';
import ConnectionsCard from '../components/kpi/ConnectionsCard';
import LatencyChart from '../components/charts/LatencyChart';
import NetworkChart from '../components/charts/NetworkChart';

const Dashboard: React.FC = () => {
  const [latencyHistory, setLatencyHistory] = useState<ChartDataPoint[]>([]);
  const [networkHistory, setNetworkHistory] = useState<NetworkChartDataPoint[]>([]);
  const [previousPacketsRecv, setPreviousPacketsRecv] = useState<number | undefined>();
  
  const maxHistoryPoints = 30; // Keep last 30 data points (1 minute at 2s interval)

  // Poll health status
  const { 
    data: healthData,
    error: healthError,
    isLoading: healthLoading
  } = usePolling<HealthResponse>({
    fetchFn: victimApi.getHealthStatus,
    interval: 2000,
    initialData: { status: 'DOWN', http_code: 0, response_time_ms: 0 },
    onError: (error) => console.error('Health polling error:', error)
  });

  // Poll system metrics
  const { 
    data: systemData,
    error: systemError,
    isLoading: systemLoading
  } = usePolling<SystemMetrics | null>({
    fetchFn: victimApi.getSystemMetrics,
    interval: 2000,
    initialData: null,
    onError: (error) => console.error('System metrics polling error:', error)
  });

  // Update history when new data arrives
  useEffect(() => {
    if (healthData && healthData.response_time_ms > 0) {
      setLatencyHistory(prev => {
        const newPoint: ChartDataPoint = {
          timestamp: Date.now() / 1000,
          value: healthData.response_time_ms
        };
        const newHistory = [...prev, newPoint];
        return newHistory.slice(-maxHistoryPoints);
      });
    }
  }, [healthData]);

  useEffect(() => {
    if (systemData) {
      setNetworkHistory(prev => {
        const newPoint: NetworkChartDataPoint = {
          timestamp: systemData.timestamp,
          rx: systemData.network_bytes_recv,
          tx: systemData.network_bytes_sent
        };
        const newHistory = [...prev, newPoint];
        return newHistory.slice(-maxHistoryPoints);
      });

      setPreviousPacketsRecv(systemData.network_packets_recv);
    }
  }, [systemData]);

  // Calculate current RPS
  const currentPacketsRecv = systemData?.network_packets_recv || 0;

  // Handle loading state
  if (healthLoading && systemLoading && !healthData && !systemData) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-700 mb-2">Loading Dashboard...</div>
          <div className="text-gray-500">Connecting to victim backend</div>
        </div>
      </div>
    );
  }

  // Handle error state
  const hasError = healthError || systemError;
  const isBackendDown = !healthData || healthData.status === 'DOWN';

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Victim Server Monitor
            </h1>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isBackendDown ? 'bg-red-500' : 'bg-green-500'
              }`} />
              <span className="text-sm text-gray-600">
                {isBackendDown ? 'Backend Down' : 'Connected'}
              </span>
            </div>
          </div>
          {hasError && (
            <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-700">
                ⚠️ Some metrics may be stale - Backend connection issues
              </p>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <StatusCard 
            status={healthData?.status || 'DOWN'} 
            httpCode={healthData?.http_code || 0}
          />
          <RPSCard 
            packetsRecv={currentPacketsRecv}
            previousPacketsRecv={previousPacketsRecv}
          />
          <LatencyCard 
            latencyMs={healthData?.response_time_ms || 0}
          />
          <ConnectionsCard 
            connections={systemData?.active_connections || 0}
            cpuPercent={systemData?.cpu_percent || 0}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <LatencyChart data={latencyHistory} />
          <NetworkChart data={networkHistory} />
        </div>

        {/* System Details */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-medium mb-4">System Details</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-500">CPU Usage</div>
              <div className="text-xl font-semibold">
                {systemData?.cpu_percent.toFixed(1)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Memory Usage</div>
              <div className="text-xl font-semibold">
                {systemData?.memory_percent.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400">
                {systemData?.memory_used_gb.toFixed(1)}GB / {systemData?.memory_total_gb.toFixed(1)}GB
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Network RX</div>
              <div className="text-xl font-semibold">
                {(systemData?.network_bytes_recv || 0) > 1024 * 1024 
                  ? `${((systemData?.network_bytes_recv || 0) / 1024 / 1024).toFixed(2)} MB`
                  : `${((systemData?.network_bytes_recv || 0) / 1024).toFixed(2)} KB`
                }
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Network TX</div>
              <div className="text-xl font-semibold">
                {(systemData?.network_bytes_sent || 0) > 1024 * 1024 
                  ? `${((systemData?.network_bytes_sent || 0) / 1024 / 1024).toFixed(2)} MB`
                  : `${((systemData?.network_bytes_sent || 0) / 1024).toFixed(2)} KB`
                }
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
