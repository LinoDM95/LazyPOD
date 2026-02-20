export type Template = {
  id: number;
  name: string;
  gelato_template_id: string;
  metadata: Record<string, unknown>;
  is_active: boolean;
};

export type DesignAsset = {
  id: number;
  file: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  created_at: string;
};

export type ProductDraft = {
  id: number;
  title: string;
  description: string;
  tags: string[];
  seo: Record<string, unknown>;
  status: 'draft' | 'queued' | 'pushed' | 'failed';
  price: string;
  template: Template;
  assets: DesignAsset[];
  created_at: string;
  updated_at: string;
};

export type IntegrationStatus = 'connected' | 'disconnected' | 'error';

export type IntegrationItem = {
  provider: 'shopify' | 'gelato';
  status: IntegrationStatus;
  errorMessage?: string | null;
  metadata: Record<string, string>;
};

export type IntegrationListResponse = {
  items: IntegrationItem[];
};
