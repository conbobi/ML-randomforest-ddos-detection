// frontend_victim/src/components/kpi/LatencyCard.tsx

import React from 'react';

interface LatencyCardProps {
  latencyMs: number;
}

const LatencyCard: React.FC<LatencyCardProps> = ({ latencyMs }) => {
  const getLatencyColor = (ms: number): string => {
    if (ms === 0) return 'text-gray-400';
    if (ms < 50) return 'text-green-600';
    if (ms < 200) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getLatencyLabel = (ms: number): string => {
    if (ms === 0) return 'No Response';
    if (ms < 50) return 'Excellent';
    if (ms < 200) return 'Good';
    return 'Poor';
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="text-sm font-medium text-gray-600 mb-2">P95 Latency</div>
      <div className={`text-3xl font-bold ${getLatencyColor(latencyMs)}`}>
        {latencyMs > 0 ? `${latencyMs.toFixed(1)}ms` : 'N/A'}
      </div>
      <div className="mt-2 text-sm text-gray-500">
        {getLatencyLabel(latencyMs)}
      </div>
    </div>
  );
};

export default LatencyCard;
