import type { ReactNode } from 'react';

type AppShellProps = {
  currentPath: string;
  onNavigate: (path: string) => void;
  children: ReactNode;
};

const navItems = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/integrations', label: 'Integrationen' },
  { path: '/settings', label: 'Settings' },
];

export function AppShell({ currentPath, onNavigate, children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto grid max-w-7xl grid-cols-1 md:grid-cols-[240px_1fr]">
        <aside className="border-b border-slate-800 p-4 md:min-h-screen md:border-b-0 md:border-r">
          <div className="mb-6 text-xl font-bold">LazyPOD</div>
          <nav className="space-y-2">
            {navItems.map((item) => {
              const active = currentPath === item.path;
              return (
                <button
                  key={item.path}
                  type="button"
                  onClick={() => onNavigate(item.path)}
                  className={`w-full rounded px-3 py-2 text-left text-sm transition ${active ? 'bg-indigo-500/30 text-indigo-100' : 'hover:bg-slate-800'}`}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>
        </aside>
        <main className="p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
}
