import { useEffect, useMemo, useState } from 'react';

import { AppShell } from './layout/AppShell';
import { DashboardPage } from './pages/DashboardPage';
import { IntegrationsPage } from './pages/IntegrationsPage';
import { SettingsPage } from './pages/SettingsPage';

const allowedPaths = new Set(['/dashboard', '/integrations', '/settings']);

function getCurrentPath() {
  const path = window.location.pathname;
  if (allowedPaths.has(path)) {
    return path;
  }
  return '/dashboard';
}

function App() {
  const [path, setPath] = useState(getCurrentPath());

  useEffect(() => {
    const handler = () => setPath(getCurrentPath());
    window.addEventListener('popstate', handler);
    return () => window.removeEventListener('popstate', handler);
  }, []);

  const page = useMemo(() => {
    if (path === '/integrations') return <IntegrationsPage />;
    if (path === '/settings') return <SettingsPage />;
    return <DashboardPage />;
  }, [path]);

  const handleNavigate = (nextPath: string) => {
    if (nextPath === path) return;
    window.history.pushState({}, '', nextPath);
    setPath(nextPath);
  };

  return <AppShell currentPath={path} onNavigate={handleNavigate}>{page}</AppShell>;
}

export default App;
