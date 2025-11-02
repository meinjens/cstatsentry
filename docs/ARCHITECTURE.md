# CStatSentry - Architektur-Dokumentation

## Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [System-Architektur](#system-architektur)
3. [Backend](#backend)
4. [Frontend](#frontend)
5. [Demo-Downloader](#demo-downloader)
6. [Infrastruktur & Deployment](#infrastruktur--deployment)
7. [Datenfluss & Patterns](#datenfluss--patterns)
8. [Sicherheit](#sicherheit)
9. [Technologie-Stack](#technologie-stack)

---

## Projektübersicht

**CStatSentry** ist ein CS2 Anti-Cheat Detection System, das automatisch Mitspieler analysiert und verdächtige Spieler identifiziert. Es nutzt eine moderne Microservices-Architektur mit React Frontend, FastAPI Backend und mehreren Datenquellen.

### Kernfunktionen

- **Steam OAuth Authentifizierung** - Sichere Anmeldung über Steam
- **Multi-Source Match-Synchronisation** - Datenabfrage von Leetify und Steam
- **Automatische Spieleranalyse** - Cheat-Detection durch Multi-Faktor-Analyse
- **Background Processing** - Asynchrone Datenverarbeitung mit Celery
- **Demo-Download Service** - Automatischer Download von CS2 Demo-Dateien
- **Dashboard & Statistiken** - Übersichtliche Darstellung verdächtiger Spieler

---

## System-Architektur

### Komponenten-Übersicht

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST
         │ JWT Auth
         ▼
┌─────────────────┐     ┌──────────────┐
│   Nginx Proxy   │────▶│  Frontend    │
│   (Port 80)     │     │  (Static)    │
└────────┬────────┘     └──────────────┘
         │
         │ Proxy /api/*
         ▼
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  FastAPI Backend│────▶│ PostgreSQL   │     │   Redis      │
│  (Port 8000)    │     │ (Port 5432)  │     │ (Port 6379)  │
└────────┬────────┘     └──────────────┘     └──────┬───────┘
         │                                            │
         │ Trigger Tasks                             │ Queue
         ▼                                            │
┌─────────────────┐                                  │
│ Celery Worker   │◀─────────────────────────────────┘
└─────────────────┘
         ▲
         │ Schedule
         │
┌─────────────────┐
│  Celery Beat    │
└─────────────────┘

┌─────────────────┐     ┌──────────────┐
│ Demo-Downloader │────▶│  PostgreSQL  │
│ (Port 3000)     │     │  (Prisma)    │
└────────┬────────┘     └──────────────┘
         │
         │ Bull Queue
         ▼
┌─────────────────┐
│     Redis       │
└─────────────────┘
```

### Externe Integrationen

- **Steam Web API** - Spielerprofil, Bans, Statistiken
- **Steam Match History** - Match-Historie via Sharecodes
- **Leetify API** - Erweiterte Match-Details
- **Steam Game Coordinator** - Demo-Downloads

---

## Backend

### Technologie-Stack

- **Framework**: FastAPI (Python 3.13)
- **Datenbank**: PostgreSQL 18 (SQLAlchemy ORM)
- **Cache/Queue**: Redis 8
- **Background Jobs**: Celery + Celery Beat
- **Authentication**: Steam OpenID + JWT
- **HTTP Client**: httpx (async)
- **Container**: Docker (Alpine Linux)

### Verzeichnisstruktur

```
backend/
├── app/
│   ├── main.py                 # FastAPI Hauptanwendung
│   ├── api/                    # API Endpoints
│   │   ├── api_v1/
│   │   │   ├── api.py          # Router-Registrierung
│   │   │   └── endpoints/      # REST Endpoints
│   │   │       ├── auth.py     # Steam OAuth & JWT
│   │   │       ├── users.py    # Benutzerverwaltung
│   │   │       ├── players.py  # Spieleranalyse
│   │   │       ├── matches.py  # Match-Verwaltung
│   │   │       ├── dashboard.py # Dashboard-Statistiken
│   │   │       └── dev.py      # Entwicklungs-Endpoints
│   │   └── deps.py             # Abhängigkeiten (Auth, DB)
│   │
│   ├── core/                   # Kernkomponenten
│   │   ├── config.py           # Pydantic Settings
│   │   ├── security.py         # JWT Token-Handling
│   │   └── celery.py           # Celery Konfiguration
│   │
│   ├── models/                 # SQLAlchemy Modelle
│   │   ├── user.py             # Benutzer (Steam-Authentifizierung)
│   │   ├── player.py           # Spieler, Bans, Analysen
│   │   ├── match.py            # Matches, MatchPlayers
│   │   └── teammate.py         # User-Teammate Beziehungen
│   │
│   ├── schemas/                # Pydantic Schemas (API)
│   ├── crud/                   # CRUD-Operationen
│   │
│   ├── services/               # Business Logic Layer
│   │   ├── steam_api.py        # Steam Web API Client
│   │   ├── steam_auth.py       # Steam OpenID Authentifizierung
│   │   ├── steam_match_history.py # Match History via Sharecodes
│   │   ├── steam_sharecode.py  # Sharecode De/Encoding
│   │   ├── leetify_api.py      # Leetify API Integration
│   │   ├── demo_downloader.py  # Demo-Download Service
│   │   ├── demo_parser.py      # Demo-Parsing
│   │   └── match_providers/    # Verschiedene Match-Datenquellen
│   │
│   ├── tasks/                  # Celery Background Tasks
│   │   ├── match_sync.py       # Multi-Source Match Sync (Orchestrator)
│   │   ├── match_sync_leetify.py # Leetify Match Sync
│   │   ├── match_sync_steam.py # Steam Match Sync
│   │   ├── player_analysis.py  # Spieler-Profilanalyse
│   │   └── steam_data_update.py # Ban-Status Updates
│   │
│   ├── analysis/               # Cheat-Detection Algorithmen
│   │   ├── aimbot_detector.py
│   │   └── wallhack_detector.py
│   │
│   └── db/                     # Datenbank-Konfiguration
│       └── session.py          # DB Session Management
│
├── alembic/                    # Datenbank-Migrationen
└── tests/                      # Backend Tests
```

### API Endpoints

#### Authentication (`/api/v1/auth`)

- `GET /steam/login` - Steam OAuth URL generieren
- `GET /steam/callback` - Steam OAuth Callback
- `POST /refresh` - Token erneuern
- `GET /me` - Aktueller Benutzer
- `POST /logout` - Abmelden

#### Users (`/api/v1/users`)

- `GET /me` - Benutzerprofil
- `PUT /me` - Profil aktualisieren
- `GET /me/teammates` - Mitspieler-Liste

#### Players (`/api/v1/players`)

- `GET /` - Verdächtige Spieler (filterable)
- `GET /{steam_id}` - Spielerdetails mit Analyse
- `GET /{steam_id}/analysis` - Analyse-Historie
- `POST /{steam_id}/analyze` - Manuelle Analyse triggern
- `POST /{steam_id}/update` - Profil von Steam API aktualisieren

#### Matches (`/api/v1/matches`)

- `GET /` - Match-Historie
- `GET /{match_id}` - Match-Details
- `POST /sync` - Manuelle Match-Synchronisation
- `GET /sync/status` - Sync-Status prüfen

#### Dashboard (`/api/v1/dashboard`)

- `GET /summary` - Dashboard-Zusammenfassung
- `GET /recent` - Kürzliche Aktivitäten
- `GET /statistics` - Statistiken & Trends

### Datenmodelle

#### User

```python
- user_id (PK)
- steam_id (unique)
- steam_name, avatar_url
- last_sync, sync_enabled
- steam_auth_code (für Match History)
- last_match_sharecode
```

#### Player

```python
- steam_id (PK)
- current_name, previous_names
- account_created, last_logoff
- profile_state, visibility_state
- cs2_hours, total_games_owned
- profile_updated, stats_updated
```

#### PlayerBan

```python
- steam_id (PK, FK)
- community_banned, vac_banned
- number_of_vac_bans
- days_since_last_ban
```

#### PlayerAnalysis

```python
- analysis_id (PK)
- steam_id (FK)
- suspicion_score (0-100)
- flags (JSON)
- confidence_level
- analysis_version
```

#### Match

```python
- match_id (PK)
- user_id (FK)
- match_date, map
- score_team1, score_team2
- sharing_code, leetify_match_id
```

### Celery Background Tasks

#### Scheduled Tasks (Celery Beat)

1. **fetch_new_matches_for_all_users** - Alle 30 Minuten
   - Orchestriert Match-Sync für alle aktiven Benutzer

2. **update_ban_status_batch** - Täglich
   - Aktualisiert VAC/Ban-Status für alle Spieler

3. **cleanup_old_data** - Täglich
   - Bereinigt alte Daten

#### On-Demand Tasks

- `fetch_user_matches(user_id)` - Multi-Source Match Sync (Orchestrator)
- `sync_leetify_matches()` - Leetify Match Sync
- `sync_steam_matches()` - Steam Match Sync
- `analyze_player_profile()` - Spieleranalyse
- `batch_analyze_players()` - Batch-Analyse

### Cheat-Detection System

Das System verwendet ein punktebasiertes Bewertungssystem (0-100 Punkte):

#### Profile Flags (max 40 Punkte)

- Neues Konto (< 30 Tage): +10
- Privates Profil: +15
- Wenige Spiele (< 5): +10
- Nur CS2: +5

#### Statistical Flags (max 40 Punkte)

- Performance-Spitzen
- Headshot-Rate-Analyse
- Konsistenzmuster
- Skill vs. Stunden Korrelation

#### Historical Flags (max 20 Punkte)

- Namensänderungshäufigkeit
- Länderwechsel
- Performance-Trends

#### Bewertungsskala

- **0-30**: Unwahrscheinlich
- **31-60**: Verdächtige Muster
- **61-80**: Hoch verdächtig
- **81-100**: Fast sicher

---

## Frontend

### Technologie-Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Package Manager**: pnpm
- **Container**: Nginx (Alpine)

### Projektstruktur

```
frontend/
├── src/
│   ├── main.tsx                # Entry Point
│   ├── App.tsx                 # Router-Konfiguration
│   ├── index.css               # Globale Styles
│   │
│   ├── components/             # Wiederverwendbare Komponenten
│   │   ├── Layout.tsx          # Haupt-Layout mit Navigation
│   │   └── ProtectedRoute.tsx  # Auth-Guard
│   │
│   ├── pages/                  # Seiten/Views
│   │   ├── Login.tsx           # Login-Seite
│   │   ├── AuthCallback.tsx    # Steam OAuth Callback
│   │   ├── Dashboard.tsx       # Hauptdashboard
│   │   ├── Players.tsx         # Spielerliste
│   │   ├── PlayerDetail.tsx    # Spielerdetails
│   │   ├── Matches.tsx         # Match-Historie
│   │   ├── MatchDetails.tsx    # Match-Details
│   │   └── Settings.tsx        # Einstellungen
│   │
│   ├── services/               # API Integration
│   │   └── api.ts              # Axios Client + API Funktionen
│   │
│   ├── contexts/               # React Context
│   │   └── AuthContext.tsx     # Authentifizierungskontext
│   │
│   └── types/                  # TypeScript Definitionen
│       └── index.ts            # Alle Interfaces
│
├── public/                     # Statische Assets
├── vite.config.ts              # Vite-Konfiguration
└── tailwind.config.js          # Tailwind-Konfiguration
```

### Routing-Struktur

```typescript
/ (Layout)
├── / → Dashboard (Protected)
├── /login → Login
├── /auth/steam/callback → AuthCallback
├── /players → Players List (Protected)
├── /players/:steamId → Player Detail (Protected)
├── /matches → Matches List (Protected)
├── /matches/:matchId → Match Details (Protected)
└── /settings → Settings (Protected)
```

### State Management

**React Query (TanStack Query)**:
- Serverseitiges State Management
- Automatisches Caching
- Background Refetching
- Optimistic Updates

**AuthContext**:
- JWT Token-Verwaltung
- Benutzerinformationen
- Authentifizierungsstatus

**LocalStorage**:
- `access_token` - JWT Token
- `user` - Benutzerinformationen

### API Service Layer

```typescript
// services/api.ts
- authAPI: getSteamLoginUrl, handleSteamCallback, getCurrentUser
- usersAPI: getProfile, updateProfile, getTeammates
- playersAPI: getPlayer, triggerPlayerAnalysis, getSuspiciousPlayers
- matchesAPI: getMatches, getMatch, triggerSync, getSyncStatus
- dashboardAPI: getSummary, getRecentActivity, getStatistics
```

### UI/UX Features

- **Responsive Design** - Mobile-first Ansatz
- **Real-time Updates** - Automatische Datenaktualisierung via React Query
- **Steam OAuth Integration** - Nahtlose Anmeldung
- **Protected Routes** - Automatische Authentifizierungsprüfung
- **Loading States & Error Handling** - Benutzerfreundliches Feedback

---

## Demo-Downloader

> **Note**: The demo-downloader has been moved to a separate repository: [Replay Hunter](https://github.com/meinjens/replay-hunter)

### Zweck

Separater Microservice zum Herunterladen von CS2 Demo-Dateien über den Steam Game Coordinator.

**Repository**: [https://github.com/meinjens/replay-hunter](https://github.com/meinjens/replay-hunter)

### Technologie-Stack

- **Runtime**: Node.js 18
- **Framework**: Express.js
- **Steam Integration**: steam-user, globaloffensive
- **Queue**: Bull (Redis-basiert)
- **Datenbank**: PostgreSQL (Prisma ORM)
- **Logging**: Winston

### Architektur

```
demo-downloader/
├── src/
│   ├── index.js              # Server Entry Point
│   ├── config.js             # Konfiguration
│   │
│   ├── routes/               # Express Routes
│   │   └── demos.js          # Demo API
│   │
│   ├── services/             # Business Logic
│   │   ├── demoService.js    # Demo-Verwaltung
│   │   ├── cleanupService.js # Auto-Cleanup
│   │   └── webhookService.js # Webhook-Benachrichtigungen
│   │
│   ├── steam/                # Steam Integration
│   │   └── gcClient.js       # Game Coordinator Client
│   │
│   ├── queue/                # Bull Queue
│   │   └── worker.js         # Background Jobs
│   │
│   └── utils/                # Hilfsfunktionen
│       ├── logger.js         # Winston Logger
│       └── errors.js         # Error Handling
│
├── prisma/
│   └── schema.prisma         # Datenbankschema
│
└── demos/                    # Demo-Speicher
```

### Datenmodell (Prisma)

```prisma
model Demo {
  id: UUID
  sharecode: String (unique)
  matchId, matchDate, map, score
  demoUrl, filePath, fileSize
  status: PENDING | FETCHING_URL | DOWNLOADING | COMPLETED | FAILED
  players: JSON
  createdAt, downloadedAt
}

model Webhook {
  id, demoId, url
  status: PENDING | SENT | FAILED
  attempts, lastAttempt, response
}
```

### Workflow

1. **Demo Request** → API Endpoint `/api/demos`
2. **Queue Job** → Bull Queue mit Redis
3. **Steam GC Connection** → Verbindung zum Game Coordinator
4. **Download** → Demo-Datei herunterladen
5. **Storage** → Lokaler Speicher (`./demos`)
6. **Webhook** → Optional: Benachrichtigung senden
7. **Cleanup** → Automatisches Löschen nach konfigurierbaren Tagen

### Features

- **Automatisches Cleanup** - Konfigurierbare Aufbewahrungsdauer
- **Webhook-Support** - Benachrichtigungen bei Fertigstellung
- **Statusverfolgung** - API-Endpunkte für Status-Abfragen
- **Persistente Queue** - Redis-basierte Job-Queue
- **Steam Session Management** - Automatische Verbindungsverwaltung

---

## Infrastruktur & Deployment

### Docker-Setup

#### Development (docker-compose.yml)

```yaml
Services:
- db: PostgreSQL 18
- redis: Redis 8 Alpine
- api: FastAPI Backend (Hot Reload)
- celery: Celery Worker
- celery-beat: Celery Scheduler
```

#### Production (docker-compose.prod.yml)

```yaml
Services:
- db: PostgreSQL 18 Alpine (Optimiert)
- redis: Redis 8 Alpine
- migration: Alembic Migrations (run-once)
- api: 2 Replicas, Rolling Updates
- celery-worker: 2 Replicas, Concurrency=4
- celery-beat: 1 Replica
- frontend: 2 Replicas, Nginx
- nginx: Load Balancer, Reverse Proxy
```

### Nginx-Konfiguration

**Features**:
- Reverse Proxy für Backend & Frontend
- Rate Limiting (API: 10r/s, Login: 1r/s)
- Gzip Compression
- Static Asset Caching (1 Jahr)
- Security Headers
- Health Checks
- SSL/TLS Ready

**Routes**:
- `/api/` → Backend (api:8000)
- `/docs` → API Dokumentation
- `/` → Frontend (frontend:80)

### Skalierung

**Horizontal**:
- API: 2+ Replicas (stateless)
- Frontend: 2+ Replicas (stateless)
- Celery Workers: 2+ Replicas

**Vertikal**:
- PostgreSQL: Connection Pooling, optimierte Settings
- Redis: Datenstruktur-Optimierung
- Celery: Thread Pool für Python 3.13

### Deployment-Strategien

#### Entwicklung

```bash
docker-compose up -d
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
# Nginx als Reverse Proxy
# Rolling Updates für API/Frontend
# Separate Migration Service
```

#### Docker Swarm (Optional)

- Traefik Integration
- Multi-Node Deployment
- Auto-Scaling

---

## Datenfluss & Patterns

### Authentifizierungs-Flow

```
1. User → Frontend: Klick auf "Login with Steam"
2. Frontend → Backend: GET /api/v1/auth/steam/login
3. Backend → Frontend: Steam OpenID URL
4. Frontend → Steam: Redirect zu Steam
5. Steam → Backend: OAuth Callback
6. Backend:
   - Verifiziert Steam OpenID
   - Holt Steam-Profildaten
   - Erstellt/Aktualisiert User
   - Generiert JWT Token
7. Backend → Frontend: Redirect mit Token + User Data
8. Frontend:
   - Speichert Token in LocalStorage
   - Setzt AuthContext
   - Redirect zu Dashboard
```

### Match-Synchronisation (Multi-Source)

```
Celery Beat (alle 30 Min)
└── fetch_new_matches_for_all_users
    └── Für jeden User:
        └── fetch_user_matches (Orchestrator)
            ├── sync_leetify_matches (parallel)
            │   ├── Leetify API Auth
            │   ├── Hole Recent Games
            │   ├── Für jedes Match:
            │   │   ├── Hole Match Details
            │   │   ├── Erstelle Match Record
            │   │   ├── Erstelle Player Records
            │   │   └── Speichere Teammate-Beziehungen
            │   └── Return Results
            │
            └── sync_steam_matches (parallel)
                ├── Steam Match History API
                ├── Iteriere Sharecodes
                ├── Erstelle Match Records
                └── Return Results
```

### Spieler-Analyse-Flow

```
Trigger (Manuell oder Automatisch)
└── analyze_player_profile (Celery Task)
    ├── Lade Player aus DB
    ├── Prüfe ob Update nötig
    ├── Falls ja:
    │   ├── Steam API: GetPlayerSummaries
    │   ├── Steam API: GetPlayerBans
    │   ├── Steam API: GetOwnedGames
    │   └── Update Player Record
    │
    ├── Berechne Suspicion Score:
    │   ├── Profile Flags (40 Punkte)
    │   ├── Statistical Flags (40 Punkte)
    │   └── Historical Flags (20 Punkte)
    │
    └── Erstelle PlayerAnalysis Record
```

### Design Patterns

#### Backend

- **Repository Pattern** - CRUD Layer für Datenbankzugriff
- **Service Layer Pattern** - Business Logic Kapselung
- **Factory Pattern** - API Client Instanzen
- **Async Context Manager** - Ressourcenverwaltung (`async with`)
- **Dependency Injection** - FastAPI Depends
- **Task Queue Pattern** - Celery für Background Jobs
- **Multi-Source Data Aggregation** - Orchestrator Pattern

#### Frontend

- **Component Composition** - Wiederverwendbare Komponenten
- **Custom Hooks** - AuthContext, useSteamAuth
- **Protected Routes Pattern** - Authentifizierungsschutz
- **API Service Layer** - Zentrale API-Kommunikation
- **Server State Management** - React Query

---

## Sicherheit

### Sicherheitsmaßnahmen

#### Backend

- JWT Token-basierte Authentifizierung
- Steam OpenID Verifikation
- CORS-Konfiguration
- Rate Limiting (Nginx)
- Security Headers (Nginx)
- Non-root Docker User
- Environment Variables für Secrets

#### Frontend

- Protected Routes
- Token-Refresh-Mechanismus
- XSS-Schutz (React)
- HTTPS-Ready

### Monitoring & Logging

- **Backend**: Python Logging (konfigurierbares Level)
- **Celery**: Task Tracking, Result Backend
- **Nginx**: Access & Error Logs
- **Demo-Downloader**: Winston Logging
- **Health Checks**: Alle Services

### Fehlerbehandlung

- **API**: Standardisierte HTTP-Fehler
- **Frontend**: Axios Interceptors
- **Celery**: Retry-Mechanismus
- **Express**: Error Handler Middleware

---

## Technologie-Stack

### Zusammenfassung

| Komponente | Technologie | Version |
|------------|-------------|---------|
| **Backend API** | FastAPI + Python | 3.13 |
| **Frontend** | React + TypeScript | 18 |
| **Build Tool** | Vite | 5 |
| **Datenbank** | PostgreSQL | 18 |
| **Cache/Queue** | Redis | 8 |
| **Background Jobs** | Celery + Celery Beat | Latest |
| **Demo-Downloader** | Node.js + Express | 18 |
| **Reverse Proxy** | Nginx | Alpine |
| **Container** | Docker + Docker Compose | Latest |
| **ORM (Backend)** | SQLAlchemy | Latest |
| **ORM (Demo)** | Prisma | Latest |
| **Styling** | Tailwind CSS | 3 |
| **State Management** | React Query | Latest |
| **Routing** | React Router | v6 |

### Externe Abhängigkeiten

1. **Steam Web API** (erforderlich)
   - Player Summaries, Bans, Games
   - Match History (mit Auth Code)

2. **Leetify API** (optional)
   - Erweiterte Match-Daten
   - Detaillierte Spielerstatistiken

3. **Steam Game Coordinator** (Demo-Downloader)
   - Demo-Download via steam-user Package

---

## Zusammenfassung

### Hauptkomponenten & Verantwortlichkeiten

| Komponente | Technologie | Verantwortlichkeit |
|------------|-------------|-------------------|
| **Backend API** | FastAPI + PostgreSQL | REST API, Authentifizierung, Datenmanagement |
| **Frontend** | React + TypeScript | Benutzeroberfläche, Dashboard, Visualisierung |
| **Celery Workers** | Celery + Redis | Background Jobs, Match-Sync, Analysen |
| **Celery Beat** | Celery Beat | Zeitgesteuerte Tasks (alle 30 Min) |
| **Demo-Downloader** | Node.js + Express | CS2 Demo-Download & -Verwaltung |
| **Nginx** | Nginx | Reverse Proxy, Load Balancing, SSL |
| **PostgreSQL** | PostgreSQL 18 | Hauptdatenbank |
| **Redis** | Redis 8 | Cache, Queue, Session |

### Architekturentscheidungen

1. **Microservices-Architektur**
   - Trennung von Backend, Frontend und Demo-Downloader
   - Unabhängige Skalierung möglich

2. **Multi-Source Data Aggregation**
   - Orchestrator Pattern für parallele Datenabfrage
   - Leetify + Steam für maximale Abdeckung

3. **Background Processing**
   - Celery für zeitintensive Tasks
   - Automatische Synchronisation alle 30 Minuten

4. **Type Safety**
   - TypeScript im Frontend
   - Pydantic im Backend
   - Klare API-Contracts

5. **Moderne DevOps**
   - Docker für alle Services
   - Multi-Stage Builds
   - Health Checks
   - Rolling Updates

### Technische Highlights

- **Python 3.13** mit Thread Pool für Celery
- **PostgreSQL 18** mit optimierten Settings
- **Redis 8** für Caching & Queue
- **React 18** mit TypeScript
- **Vite 5** für schnelles Building
- **Docker Multi-Stage Builds** für optimale Image-Größe
- **Horizontale Skalierung** - Alle Services können repliziert werden
- **Multi-Source Data** - Leetify und Steam Integration

---

## Fazit

CStatSentry ist eine professionell strukturierte Anwendung mit klarer Trennung der Verantwortlichkeiten, modernem Tech-Stack und durchdachter Architektur. Das System nutzt mehrere Datenquellen (Steam, Leetify), verarbeitet Daten asynchron im Hintergrund und bietet eine reaktive Benutzeroberfläche. Die Cheat-Detection erfolgt durch Multi-Faktor-Analyse von Profildaten, Statistiken und historischen Mustern.

Die Architektur ist:
- **Skalierbar** - Horizontale Skalierung aller Komponenten
- **Wartbar** - Klare Strukturierung und Patterns
- **Sicher** - Moderne Authentifizierung und Sicherheitsmaßnahmen
- **Performant** - Asynchrone Verarbeitung und Caching
- **Erweiterbar** - Service Layer Pattern ermöglicht einfache Erweiterungen
