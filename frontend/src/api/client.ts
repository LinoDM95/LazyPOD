import type { DesignAsset, ProductDraft, Template } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
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
};
