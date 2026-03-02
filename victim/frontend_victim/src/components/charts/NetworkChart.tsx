// frontend_victim/src/components/charts/NetworkChart.tsx

import React from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Area,
  ComposedChart
} from 'recharts';
import { NetworkChartDataPoint } from '../../types/victimTypes';

interface NetworkChartProps {
  data: NetworkChartDataPoint[];
  height?: number;
}

const NetworkChart: React.FC<NetworkChartProps> = ({ data, height = 300 }) => {
  const formatTime = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  return (
    <div className="bg-white p-4 rounded-lg border">
      <h3 className="text-lg font-medium mb-4">Network Traffic</h3>
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={formatTime}
            stroke="#6b7280"
            fontSize={12}
          />
          <YAxis 
            stroke="#6b7280"
            fontSize={12}
            tickFormatter={formatBytes}
            label={{ 
              value: 'Bytes/sec', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#6b7280', fontSize: 12 }
            }}
          />
          <Tooltip
            labelFormatter={(label) => formatTime(Number(label))}
            formatter={(value: number, name: string) => {
              const formattedValue = formatBytes(value);
              const label = name === 'rx' ? 'RX' : 'TX';
              return [formattedValue, label];
            }}
            contentStyle={{ backgroundColor: '#1f2937', color: '#fff', border: 'none' }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="rx"
            name="RX (Received)"
            fill="#3b82f6"
            stroke="#2563eb"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="tx"
            name="TX (Sent)"
            fill="#10b981"
            stroke="#059669"
            fillOpacity={0.3}
            strokeWidth={2}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default NetworkChart;
