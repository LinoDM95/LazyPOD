# LazyPOD MVP

## Repo Analyse (bestehende Struktur)
- `backend/backend` ist ein bestehendes Django-Projekt mit `manage.py`, `config/settings.py` und App-Ordnern (`core`, `shopify`, `gelato`).
- `frontend` ist eine bestehende Vite + React + TypeScript App.
- Vorher gab es kein funktionales Docker-Compose Setup im Root.

## MVP Features
- Backend (Django + DRF + Celery) mit Endpoints:
  - `GET /api/health`
  - `GET /api/templates`
  - `POST /api/assets/upload`
  - `POST /api/drafts/bulk`
  - `GET /api/drafts`
  - `GET /api/drafts/{id}`
  - `POST /api/drafts/{id}/push`
- Integrationen:
  - `GET /api/integrations`
  - `POST /api/integrations/gelato`
  - `DELETE /api/integrations/gelato`
  - `POST /api/integrations/shopify/start`
  - `GET /api/integrations/shopify/callback`
  - `DELETE /api/integrations/shopify`
  - `POST /api/integrations/shopify/test`
- API Docs via drf-spectacular: `GET /api/docs`
- Frontend mit AppShell + Seiten:
  - Dashboard (Placeholder)
  - Integrationen (Shopify + Gelato Management)
  - Settings (Placeholder)
- Mock ist standardmäßig aktiv (`USE_MOCK_APIS=true`).

## Start (copy/paste)
```bash
cp .env.example .env
docker compose up --build
```

## URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Health: http://localhost:8000/api/health
- API Docs: http://localhost:8000/api/docs

## Integrationen verbinden
1. `.env` setzen:
   - `APP_URL=http://localhost:5173`
   - `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET`, `SHOPIFY_SCOPES`
2. Shopify App Callback URL in Shopify setzen auf:
   - `http://localhost:8000/api/integrations/shopify/callback`
3. Frontend öffnen und zu **Integrationen** navigieren.
4. **Shopify verbinden**:
   - Shop-Domain eingeben (`example` oder `example.myshopify.com`)
   - OAuth-Redirect bestätigen
5. **Gelato verbinden**:
   - API-Key im Modal einfügen
   - Serverseitige Validierung läuft über `GET https://product.gelatoapis.com/v3/catalogs`
6. Optional Shopify mit **Verbindung testen** prüfen.

> Hinweis: Zugangsdaten werden ausschließlich serverseitig gespeichert und nie an das Frontend zurückgegeben.

## Tests
Backend (im Container):
```bash
docker compose exec backend pytest
```

Frontend (im Container):
```bash
docker compose exec frontend npm run test
```
