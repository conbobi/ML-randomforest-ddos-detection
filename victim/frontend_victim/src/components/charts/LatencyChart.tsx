// frontend_victim/src/components/charts/LatencyChart.tsx

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { ChartDataPoint } from '../../types/victimTypes';

interface LatencyChartProps {
  data: ChartDataPoint[];
  height?: number;
}

const LatencyChart: React.FC<LatencyChartProps> = ({ data, height = 300 }) => {
  const formatTime = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatLatency = (ms: number): string => {
    return `${ms.toFixed(1)}ms`;
  };

  return (
    <div className="bg-white p-4 rounded-lg border">
      <h3 className="text-lg font-medium mb-4">Response Time History</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
            label={{ 
              value: 'Latency (ms)', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#6b7280', fontSize: 12 }
            }}
          />
          <Tooltip
            labelFormatter={(label) => formatTime(Number(label))}
            formatter={(value: number) => [formatLatency(value), 'Latency']}
            contentStyle={{ backgroundColor: '#1f2937', color: '#fff', border: 'none' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            name="Response Time"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#3b82f6' }}
          />
          {/* Threshold lines */}
          <Line
            type="monotone"
            dataKey={() => 50}
            name="Excellent (<50ms)"
            stroke="#10b981"
            strokeDasharray="5 5"
            strokeWidth={1}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey={() => 200}
            name="Warning (>200ms)"
            stroke="#ef4444"
            strokeDasharray="5 5"
            strokeWidth={1}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LatencyChart;
