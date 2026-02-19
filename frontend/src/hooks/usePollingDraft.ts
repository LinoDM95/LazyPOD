import { useQuery } from '@tanstack/react-query';

import { api } from '../api/client';

export function usePollingDraft(draftId: number | null) {
  return useQuery({
    queryKey: ['draft', draftId],
    queryFn: () => api.draft(draftId as number),
    enabled: Boolean(draftId),
    refetchInterval: (query) => (query.state.data?.status === 'queued' ? 1500 : false),
  });
}
