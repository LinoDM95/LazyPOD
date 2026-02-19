# Terminal-Befehle zum lokalen Start von LazyPOD

Diese Datei enthält die minimalen Befehle, um das Projekt lokal zu starten.

## Voraussetzungen
- Docker + Docker Compose installiert
- Port `5173` (Frontend), `8000` (Backend), `5432` (Postgres), `6379` (Redis) frei

## 1) Ins Projekt wechseln
```bash
cd /workspace/LazyPOD
```

## 2) Environment-Datei anlegen
```bash
cp .env.example .env
```

## 3) Alle Services bauen und starten
```bash
docker compose up --build
```

## 4) Wichtige URLs öffnen
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Health: http://localhost:8000/api/health
- API Docs: http://localhost:8000/api/docs

## 5) Tests in laufenden Containern ausführen (optional)
Backend:
```bash
docker compose exec backend pytest
```

Frontend:
```bash
docker compose exec frontend npm run test
```

## 6) Services stoppen
```bash
docker compose down
```

## 7) (Optional) Volumes inkl. DB löschen
```bash
docker compose down -v
```
