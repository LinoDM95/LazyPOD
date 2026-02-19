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
- API Docs via drf-spectacular: `GET /api/docs`
- Frontend zeigt:
  - Running-Status + Health
  - Templates Liste
  - Upload + Draft Create
  - Draft Detail + Push + Status Polling
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

## Tests
Backend (im Container):
```bash
docker compose exec backend pytest
```

Frontend (im Container):
```bash
docker compose exec frontend npm run test
```
