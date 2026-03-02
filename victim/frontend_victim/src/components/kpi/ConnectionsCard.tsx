// frontend_victim/src/components/kpi/ConnectionsCard.tsx

import React from 'react';

interface ConnectionsCardProps {
  connections: number;
  cpuPercent: number;
}

const ConnectionsCard: React.FC<ConnectionsCardProps> = ({ connections, cpuPercent }) => {
  const getConnectionStatus = (conn: number): string => {
    if (conn > 1000) return 'Critical';
    if (conn > 500) return 'High';
    if (conn > 100) return 'Normal';
    return 'Low';
  };

  const getStatusColor = (conn: number): string => {
    if (conn > 1000) return 'text-red-600';
    if (conn > 500) return 'text-orange-600';
    if (conn > 100) return 'text-blue-600';
    return 'text-green-600';
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="text-sm font-medium text-gray-600 mb-2">Active Connections</div>
      <div className={`text-3xl font-bold ${getStatusColor(connections)}`}>
        {connections.toLocaleString()}
      </div>
      <div className="mt-2 flex justify-between text-sm">
        <span className="text-gray-500">Status:</span>
        <span className={getStatusColor(connections)}>
          {getConnectionStatus(connections)}
        </span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-500">CPU:</span>
        <span className={cpuPercent > 80 ? 'text-red-600' : 'text-gray-700'}>
          {cpuPercent.toFixed(1)}%
        </span>
      </div>
    </div>
  );
};

export default ConnectionsCard;
