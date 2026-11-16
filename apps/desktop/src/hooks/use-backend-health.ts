import { useQuery } from '@tanstack/react-query';
import { apiClient, BackendHealth } from '@/lib/api-client';

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting';

export function useBackendHealth() {
  const query = useQuery<BackendHealth, Error>({
    queryKey: ['backend-health'],
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 3000,
    retry: 2,
    retryDelay: 1000,
  });

  let connectionStatus: ConnectionStatus = 'connecting';
  if (query.isSuccess) {
    connectionStatus = 'connected';
  } else if (query.isError) {
    connectionStatus = 'disconnected';
  } else if (query.isLoading) {
    connectionStatus = 'connecting';
  }

  return {
    ...query,
    connectionStatus,
    health: query.data,
  };
}
