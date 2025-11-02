# CStatSentry Documentation

Willkommen zur CStatSentry Dokumentation! Hier findest du alle technischen Informationen, Anleitungen und Guides für Entwickler und Benutzer.

## 📚 Dokumentationsübersicht

### Für Entwickler

#### 🏗️ [Architecture Guide](ARCHITECTURE.md)
Detaillierte Übersicht über die Systemarchitektur, Design Patterns und technische Entscheidungen.

**Inhalt:**
- Projektübersicht und Kernfunktionen
- System-Architektur mit Komponentendiagrammen
- Backend-Architektur (FastAPI, Celery, PostgreSQL)
- Frontend-Architektur (React, TypeScript, Vite)
- Demo-Downloader Service
- Infrastruktur & Deployment
- Datenfluss & Design Patterns
- Sicherheitskonzepte
- Technologie-Stack Übersicht

#### ✅ [Features & TODO List](FEATURES_TODO.md)
Vollständige Feature-Übersicht mit Status und Roadmap.

**Inhalt:**
- ~60 fertiggestellte Features
- ~8 Features in Arbeit
- ~150+ geplante Features
- Priorisierte Roadmap (Q1-Q4 2025)
- Code TODOs mit Referenzen
- 18 Feature-Kategorien

**Kategorien:**
- Authentifizierung & Benutzerverwaltung
- Match-Synchronisation
- Spieleranalyse & Cheat-Detection
- Dashboard & Statistiken
- Demo-Downloader & Parsing (moved to [Replay Hunter](https://github.com/meinjens/replay-hunter) 🎯)
- Testing & Qualität
- Performance & Optimierung
- Deployment & DevOps
- Und weitere...

#### 🧪 [TDD Guide](TDD_GUIDE.md)
Test-Driven Development Workflow und Best Practices.

**Inhalt:**
- Quick Start für Tests
- TDD Workflow (Red-Green-Refactor)
- Verfügbare Test Fixtures
- Test Kategorien (Unit, Integration, etc.)
- Spezifische Tests ausführen
- Authentication in Tests
- Mocking External Services
- Best Practices

#### 🔗 [Integration Testing](INTEGRATION_TESTING.md)
Testing mit Mock Services und Docker-basierter Testumgebung.

**Inhalt:**
- Mock Services Architektur
- Quick Start Guide
- Mock Steam API Features
- Usage Examples
- Development Workflow
- Debugging & Troubleshooting

#### ⚙️ [Setup Guide](SETUP.md)
Detaillierte Konfigurationsanleitung für Entwicklung und Production.

**Inhalt:**
- Entwicklungsumgebung aufsetzen
- Umgebungsvariablen konfigurieren
- Steam API Setup
- Leetify API Integration
- Datenbank-Setup
- Production Deployment

#### 🔌 [API Documentation](API.md)
REST API Referenz und Endpoint-Dokumentation.

**Inhalt:**
- API Endpoints Übersicht
- Authentication Flow
- Request/Response Beispiele
- Error Handling
- Rate Limiting

---

## 🚀 Quick Links

### Getting Started

1. **Erste Schritte**: Lies die [Hauptdokumentation](../README.md)
2. **Entwicklung starten**: Folge dem [Setup Guide](SETUP.md)
3. **Architektur verstehen**: Siehe [Architecture Guide](ARCHITECTURE.md)
4. **Features erkunden**: Siehe [Features & TODO List](FEATURES_TODO.md)

### Entwicklung

- **Tests schreiben**: [TDD Guide](TDD_GUIDE.md)
- **Integration Tests**: [Integration Testing](INTEGRATION_TESTING.md)
- **API nutzen**: [API Documentation](API.md)
- **Production Deploy**: [Setup Guide](SETUP.md) + [Architecture Guide](ARCHITECTURE.md)

---

## 📖 Weitere Ressourcen

### Online Dokumentation

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **GitHub Repository**: https://github.com/meinjens/cstatsentry

### Externe Dokumentation

- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [React Dokumentation](https://react.dev/)
- [Celery Dokumentation](https://docs.celeryq.dev/)
- [Steam Web API Dokumentation](https://developer.valvesoftware.com/wiki/Steam_Web_API)
- [PostgreSQL Dokumentation](https://www.postgresql.org/docs/)

---

## 🤝 Beitragen

Wenn du zur Dokumentation beitragen möchtest:

1. Dokumentationsdateien sind in Markdown geschrieben
2. Folge dem bestehenden Format und Stil
3. Füge Links zu verwandten Dokumenten hinzu
4. Teste alle Code-Beispiele
5. Erstelle einen Pull Request

---

## 📝 Dokumentations-Richtlinien

### Markdown-Format

- Nutze GitHub-Flavored Markdown
- Füge Code-Beispiele in Sprachblöcken ein (\`\`\`python, \`\`\`typescript, etc.)
- Nutze Emojis sparsam für bessere Lesbarkeit
- Verlinke verwandte Dokumente

### Code-Beispiele

- Verwende realistische Beispiele
- Füge Kommentare für komplexe Logik hinzu
- Zeige sowohl Success- als auch Error-Cases
- Halte Beispiele kurz und fokussiert

### Updates

- Aktualisiere Dokumentation bei Code-Änderungen
- Markiere veraltete Informationen
- Füge Versionsnummern hinzu wo sinnvoll
- Dokumentiere Breaking Changes

---

**Letzte Aktualisierung**: 2025-02-11
**Version**: 1.0
