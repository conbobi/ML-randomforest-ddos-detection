// frontend_victim/src/hooks/usePolling.ts

import { useEffect, useState, useRef, useCallback } from 'react';

interface UsePollingOptions<T> {
  fetchFn: () => Promise<T>;
  interval: number;
  initialData?: T;
  onError?: (error: Error) => void;
}

export function usePolling<T>({ 
  fetchFn, 
  interval, 
  initialData,
  onError 
}: UsePollingOptions<T>) {
  const [data, setData] = useState<T | undefined>(initialData);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isPolling, setIsPolling] = useState<boolean>(true);
  
  const timeoutRef = useRef<NodeJS.Timeout>();
  const mountedRef = useRef<boolean>(true);
  const fetchCountRef = useRef<number>(0);

  const fetchData = useCallback(async () => {
    if (!mountedRef.current || !isPolling) return;
    
    const currentFetchId = ++fetchCountRef.current;
    
    try {
      setIsLoading(true);
      const result = await fetchFn();
      
      // Only update if this is the most recent fetch
      if (mountedRef.current && currentFetchId === fetchCountRef.current) {
        setData(result);
        setError(null);
      }
    } catch (err) {
      if (mountedRef.current && currentFetchId === fetchCountRef.current) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        onError?.(error);
      }
    } finally {
      if (mountedRef.current && currentFetchId === fetchCountRef.current) {
        setIsLoading(false);
      }
    }
  }, [fetchFn, onError, isPolling]);

  const startPolling = useCallback(() => {
    setIsPolling(true);
  }, []);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  const refetch = useCallback(async () => {
    if (!mountedRef.current) return;
    await fetchData();
  }, [fetchData]);

  // Initial fetch and polling setup
  useEffect(() => {
    mountedRef.current = true;
    
    // Initial fetch
    fetchData();

    // Setup polling interval
    const intervalId = setInterval(() => {
      if (mountedRef.current && isPolling) {
        fetchData();
      }
    }, interval);

    return () => {
      mountedRef.current = false;
      clearInterval(intervalId);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [fetchData, interval, isPolling]);

  return {
    data,
    error,
    isLoading,
    isPolling,
    startPolling,
    stopPolling,
    refetch
  };
}
