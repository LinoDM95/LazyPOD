import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { api } from '../api/client';
import { IntegrationCard } from '../components/IntegrationCard';
import { Modal } from '../components/Modal';
import type { IntegrationItem } from '../types/api';

function normalizeShopDomain(value: string): string {
  const cleaned = value.trim().toLowerCase();
  if (!cleaned) return '';
  if (cleaned.includes('.')) return cleaned;
  return `${cleaned}.myshopify.com`;
}

function fallbackItem(provider: IntegrationItem['provider']): IntegrationItem {
  return {
    provider,
    status: 'disconnected',
    metadata: {},
    errorMessage: null,
  };
}

export function IntegrationsPage() {
  const queryClient = useQueryClient();
  const [shopifyModalOpen, setShopifyModalOpen] = useState(false);
  const [gelatoModalOpen, setGelatoModalOpen] = useState(false);
  const [disconnectTarget, setDisconnectTarget] = useState<IntegrationItem['provider'] | null>(null);
  const [shopDomain, setShopDomain] = useState('');
  const [gelatoKey, setGelatoKey] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const integrationsQuery = useQuery({ queryKey: ['integrations'], queryFn: api.integrations });

  const refetchIntegrations = () => queryClient.invalidateQueries({ queryKey: ['integrations'] });

  const gelatoConnectMutation = useMutation({
    mutationFn: api.connectGelato,
    onSuccess: async () => {
      setMessage('Gelato verbunden.');
      setGelatoModalOpen(false);
      setGelatoKey('');
      await refetchIntegrations();
    },
    onError: (error: Error) => setMessage(error.message),
  });

  const gelatoDisconnectMutation = useMutation({
    mutationFn: api.disconnectGelato,
    onSuccess: async () => {
      setMessage('Gelato getrennt.');
      setDisconnectTarget(null);
      await refetchIntegrations();
    },
    onError: (error: Error) => setMessage(error.message),
  });

  const shopifyStartMutation = useMutation({
    mutationFn: api.startShopify,
    onSuccess: ({ redirectUrl }) => {
      window.location.href = redirectUrl;
    },
    onError: (error: Error) => setMessage(error.message),
  });

  const shopifyDisconnectMutation = useMutation({
    mutationFn: api.disconnectShopify,
    onSuccess: async () => {
      setMessage('Shopify getrennt.');
      setDisconnectTarget(null);
      await refetchIntegrations();
    },
    onError: (error: Error) => setMessage(error.message),
  });

  const shopifyTestMutation = useMutation({
    mutationFn: api.testShopify,
    onSuccess: async () => {
      setMessage('Shopify Verbindung erfolgreich getestet.');
      await refetchIntegrations();
    },
    onError: (error: Error) => setMessage(error.message),
  });

  const shopifyItem = useMemo(
    () => integrationsQuery.data?.items.find((item) => item.provider === 'shopify') ?? fallbackItem('shopify'),
    [integrationsQuery.data?.items],
  );
  const gelatoItem = useMemo(
    () => integrationsQuery.data?.items.find((item) => item.provider === 'gelato') ?? fallbackItem('gelato'),
    [integrationsQuery.data?.items],
  );

  return (
    <section>
      <h1 className="mb-2 text-2xl font-bold">Integrationen</h1>
      <p className="mb-6 text-slate-300">Verbinde externe Tools sicher über serverseitige Credentials.</p>
      {message && <div className="mb-4 rounded border border-slate-700 bg-slate-900 p-3 text-sm">{message}</div>}

      <div className="grid gap-4 lg:grid-cols-2">
        <IntegrationCard
          title="Shopify"
          description="OAuth-Verbindung für Shop Sync und Produkt-Push"
          item={shopifyItem}
          loading={shopifyStartMutation.isPending || shopifyDisconnectMutation.isPending || shopifyTestMutation.isPending}
          onConnect={() => setShopifyModalOpen(true)}
          onDisconnect={() => setDisconnectTarget('shopify')}
          onTest={() => shopifyTestMutation.mutate()}
        />

        <IntegrationCard
          title="Gelato"
          description="Serverseitige API-Key Verbindung für Produkt- und Katalogzugriffe"
          item={gelatoItem}
          loading={gelatoConnectMutation.isPending || gelatoDisconnectMutation.isPending}
          onConnect={() => setGelatoModalOpen(true)}
          onDisconnect={() => setDisconnectTarget('gelato')}
        />
      </div>

      <Modal title="Shopify verbinden" open={shopifyModalOpen} onClose={() => setShopifyModalOpen(false)}>
        <form
          className="space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            const normalized = normalizeShopDomain(shopDomain);
            if (!normalized || !normalized.endsWith('.myshopify.com')) {
              setMessage('Bitte gültige Shop Domain eingeben (example oder example.myshopify.com).');
              return;
            }
            shopifyStartMutation.mutate(normalized);
          }}
        >
          <label className="block text-sm">
            Shop-Domain
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2"
              placeholder="example oder example.myshopify.com"
              value={shopDomain}
              onChange={(event) => setShopDomain(event.target.value)}
            />
          </label>
          <button className="rounded bg-indigo-500 px-3 py-2 text-sm" type="submit" disabled={shopifyStartMutation.isPending}>
            Verbinden
          </button>
        </form>
      </Modal>

      <Modal title="Gelato API-Key speichern" open={gelatoModalOpen} onClose={() => setGelatoModalOpen(false)}>
        <form
          className="space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            const key = gelatoKey.trim();
            if (!key) {
              setMessage('API key darf nicht leer sein.');
              return;
            }
            gelatoConnectMutation.mutate(key);
          }}
        >
          <label className="block text-sm">
            API-Key
            <input
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2"
              value={gelatoKey}
              onChange={(event) => setGelatoKey(event.target.value)}
              type="password"
              placeholder="Gelato API-Key"
            />
          </label>
          <button className="rounded bg-indigo-500 px-3 py-2 text-sm" type="submit" disabled={gelatoConnectMutation.isPending}>
            Speichern
          </button>
        </form>
      </Modal>

      <Modal title="Verbindung trennen" open={disconnectTarget !== null} onClose={() => setDisconnectTarget(null)}>
        <div className="space-y-4 text-sm">
          <p>Bist du sicher, dass du {disconnectTarget} trennen möchtest?</p>
          <div className="flex gap-2">
            <button type="button" className="rounded border border-slate-700 px-3 py-2" onClick={() => setDisconnectTarget(null)}>
              Abbrechen
            </button>
            <button
              type="button"
              className="rounded bg-rose-600 px-3 py-2"
              onClick={() => {
                if (disconnectTarget === 'shopify') {
                  shopifyDisconnectMutation.mutate();
                  return;
                }
                gelatoDisconnectMutation.mutate();
              }}
            >
              Trennen
            </button>
          </div>
        </div>
      </Modal>
    </section>
  );
}
