// frontend_victim/src/components/kpi/StatusCard.tsx

import React from 'react';
import { HealthStatus } from '../../types/victimTypes';

interface StatusCardProps {
  status: HealthStatus;
  httpCode: number;
}

const StatusCard: React.FC<StatusCardProps> = ({ status, httpCode }) => {
  const isHealthy = status === 'HEALTHY';
  
  return (
    <div className={`rounded-lg border p-6 ${
      isHealthy ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
    }`}>
      <div className="text-sm font-medium text-gray-600 mb-2">Service Status</div>
      <div className="flex items-center justify-between">
        <div className={`text-2xl font-bold ${
          isHealthy ? 'text-green-600' : 'text-red-600'
        }`}>
          {status}
        </div>
        <div className={`text-4xl ${isHealthy ? 'text-green-500' : 'text-red-500'}`}>
          {isHealthy ? '✅' : '❌'}
        </div>
      </div>
      <div className="mt-2 text-sm text-gray-500">
        HTTP {httpCode > 0 ? httpCode : 'No Response'}
      </div>
    </div>
  );
};

export default StatusCard;
