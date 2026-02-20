import type { DesignAsset, IntegrationListResponse, ProductDraft, Template } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: 'include',
  });

  if (!response.ok) {
    let detail = `API error ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail ?? detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  templates: () => request<Template[]>('/templates'),
  drafts: () => request<ProductDraft[]>('/drafts'),
  draft: (id: number) => request<ProductDraft>(`/drafts/${id}`),
  uploadAssets: async (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    return request<DesignAsset[]>('/assets/upload', { method: 'POST', body: formData });
  },
  createDrafts: (payload: {
    drafts: Array<{
      template_id: number;
      title: string;
      description?: string;
      price: string;
      tags?: string[];
      asset_ids: number[];
    }>;
  }) => request<ProductDraft[]>('/drafts/bulk', { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } }),
  pushDraft: (id: number) => request<{ task_id: string; draft_id: number }>(`/drafts/${id}/push`, { method: 'POST' }),
  integrations: () => request<IntegrationListResponse>('/integrations'),
  connectGelato: (apiKey: string) => request<{ ok: boolean }>('/integrations/gelato', {
    method: 'POST',
    body: JSON.stringify({ apiKey }),
    headers: { 'Content-Type': 'application/json' },
  }),
  disconnectGelato: () => request<void>('/integrations/gelato', { method: 'DELETE' }),
  startShopify: (shopDomain: string) => request<{ redirectUrl: string }>('/integrations/shopify/start', {
    method: 'POST',
    body: JSON.stringify({ shopDomain }),
    headers: { 'Content-Type': 'application/json' },
  }),
  disconnectShopify: () => request<void>('/integrations/shopify', { method: 'DELETE' }),
  testShopify: () => request<{ ok: boolean }>('/integrations/shopify/test', { method: 'POST' }),
};
