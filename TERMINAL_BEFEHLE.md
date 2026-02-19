# Terminal-Befehle zum lokalen Start von LazyPOD

Diese Datei enthält die Befehle, um das Projekt lokal zu starten – inklusive Docker-Installation.

## 0) Docker installieren (falls noch nicht vorhanden)

> Wähle **eine** passende Variante für dein Betriebssystem.

### Ubuntu/Debian (apt, offizielles Docker-Repo)
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Optional ohne `sudo`:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### macOS / Windows
- Installiere **Docker Desktop**: https://www.docker.com/products/docker-desktop/

### Installation prüfen
```bash
docker --version
docker compose version
```

---

## 1) Voraussetzungen
- Docker + Docker Compose installiert
- Ports `5173` (Frontend), `8000` (Backend), `5432` (Postgres), `6379` (Redis) frei

## 2) Ins Projekt wechseln
```bash
cd /workspace/LazyPOD
```

## 3) Environment-Datei anlegen
```bash
cp .env.example .env
```

## 4) Alle Services bauen und starten
```bash
docker compose up --build
```

## 5) Wichtige URLs öffnen
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Health: http://localhost:8000/api/health
- API Docs: http://localhost:8000/api/docs

## 6) Tests in laufenden Containern ausführen (optional)
Backend:
```bash
docker compose exec backend pytest
```

Frontend:
```bash
docker compose exec frontend npm run test
```

## 7) Services stoppen
```bash
docker compose down
```

## 8) (Optional) Volumes inkl. DB löschen
```bash
docker compose down -v
```
