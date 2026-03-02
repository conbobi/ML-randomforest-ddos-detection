// frontend_victim/src/api/victimApi.ts

import axios from 'axios';
import { HealthResponse, SystemMetrics } from '../types/victimTypes';

const API_BASE_URL = '/api';

export const victimApi = {
  async getHealthStatus(): Promise<HealthResponse> {
    try {
      const response = await axios.get<HealthResponse>(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch health status:', error);
      // Return a default DOWN status when backend is unreachable
      return {
        status: 'DOWN',
        http_code: 0,
        response_time_ms: 0
      };
    }
  },

  async getSystemMetrics(): Promise<SystemMetrics | null> {
    try {
      const response = await axios.get<SystemMetrics>(`${API_BASE_URL}/system`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
      return null;
    }
  }
};
