// frontend_victim/vite.config.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001, // Different from IDS frontend
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        timeout: 5000,
        proxyTimeout: 5000
      }
    }
  },
  preview: {
    port: 3001
  }
});
