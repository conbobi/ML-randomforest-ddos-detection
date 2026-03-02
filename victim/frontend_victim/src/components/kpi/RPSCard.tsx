// frontend_victim/src/components/kpi/RPSCard.tsx

import React, { useEffect, useState } from 'react';

interface RPSCardProps {
  packetsRecv: number;
  previousPacketsRecv?: number;
}

const RPSCard: React.FC<RPSCardProps> = ({ packetsRecv, previousPacketsRecv }) => {
  const [rps, setRps] = useState<number>(0);
  const [trend, setTrend] = useState<'up' | 'down' | 'stable'>('stable');

  useEffect(() => {
    if (previousPacketsRecv !== undefined && previousPacketsRecv > 0) {
      const packetDelta = packetsRecv - previousPacketsRecv;
      const calculatedRps = Math.max(0, packetDelta / 2); // /2 because polling every 2 seconds
      setRps(calculatedRps);
      
      if (calculatedRps > 1000) setTrend('up');
      else if (calculatedRps < 100) setTrend('down');
      else setTrend('stable');
    }
  }, [packetsRecv, previousPacketsRecv]);

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="text-sm font-medium text-gray-600 mb-2">Requests/sec</div>
      <div className="text-3xl font-bold text-gray-900">
        {rps.toFixed(1)}
      </div>
      <div className="mt-2 flex items-center text-sm">
        {trend === 'up' && (
          <>
            <span className="text-red-500 mr-1">↑</span>
            <span className="text-red-600">High traffic</span>
          </>
        )}
        {trend === 'down' && (
          <>
            <span className="text-green-500 mr-1">↓</span>
            <span className="text-green-600">Low traffic</span>
          </>
        )}
        {trend === 'stable' && (
          <>
            <span className="text-blue-500 mr-1">→</span>
            <span className="text-blue-600">Normal</span>
          </>
        )}
      </div>
    </div>
  );
};

export default RPSCard;
