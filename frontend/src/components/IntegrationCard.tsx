import type { IntegrationItem } from '../types/api';

type IntegrationCardProps = {
  title: string;
  description: string;
  item: IntegrationItem;
  loading?: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onTest?: () => void;
};

const statusStyles: Record<IntegrationItem['status'], string> = {
  connected: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
  disconnected: 'bg-slate-700/50 text-slate-200 border-slate-600',
  error: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
};

export function IntegrationCard({ title, description, item, loading, onConnect, onDisconnect, onTest }: IntegrationCardProps) {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">{title}</h2>
          <p className="text-sm text-slate-300">{description}</p>
        </div>
        <span className={`rounded border px-2 py-1 text-xs uppercase tracking-wide ${statusStyles[item.status]}`}>
          {item.status}
        </span>
      </div>

      <div className="mb-4 min-h-12 rounded border border-slate-800 bg-slate-950/50 p-3 text-sm text-slate-300">
        {item.status === 'connected' && item.provider === 'shopify' && item.metadata.shopDomain && (
          <div>Shop: {item.metadata.shopDomain}</div>
        )}
        {item.status === 'connected' && item.provider === 'gelato' && item.metadata.lastVerified && (
          <div>Last verified: {new Date(item.metadata.lastVerified).toLocaleString()}</div>
        )}
        {item.errorMessage && <div className="text-rose-300">{item.errorMessage}</div>}
        {!item.errorMessage && !item.metadata.shopDomain && !item.metadata.lastVerified && <div>Keine zusätzlichen Metadaten.</div>}
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onConnect}
          disabled={loading}
          className="rounded bg-indigo-500 px-3 py-2 text-sm font-medium hover:bg-indigo-400 disabled:opacity-60"
        >
          Verbinden
        </button>
        <button
          type="button"
          onClick={onDisconnect}
          disabled={loading || item.status === 'disconnected'}
          className="rounded border border-slate-700 px-3 py-2 text-sm hover:bg-slate-800 disabled:opacity-60"
        >
          Trennen
        </button>
        {onTest && (
          <button
            type="button"
            onClick={onTest}
            disabled={loading || item.status === 'disconnected'}
            className="rounded border border-emerald-700 px-3 py-2 text-sm text-emerald-200 hover:bg-emerald-950 disabled:opacity-60"
          >
            Verbindung testen
          </button>
        )}
      </div>
    </section>
  );
}
