# StatSentry 🛡️

**CS2 Anti-Cheat Detection System** - Automated teammate analysis for suspicious player identification.

[![CI/CD Pipeline](https://github.com/yourusername/statsentry/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/statsentry/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Swarm](https://img.shields.io/badge/Docker%20Swarm-Supported-green)](https://docs.docker.com/engine/swarm/)

## ✨ Features

- 🔐 **Steam OAuth Authentication** - Secure login via Steam OpenID
- 🎯 **Automated Match Analysis** - Continuous monitoring of CS2 teammates
- 🚨 **Suspicious Player Detection** - Advanced scoring algorithm with multiple detection criteria
- 📊 **Real-time Dashboard** - Live updates and comprehensive analytics
- ⚡ **Background Processing** - Celery-powered asynchronous job system
- 🔄 **Auto-Sync** - Periodic match synchronization every 30 minutes
- 🐳 **Production Ready** - Docker Swarm deployment with high availability

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │  PostgreSQL     │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│  (Database)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Celery      │◄──►│     Redis       │
                       │ (Background)    │    │   (Cache)       │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/statsentry.git
cd statsentry

# Start with Docker Compose
docker-compose up -d

# Or use the setup script
./scripts/start.sh
```

**Access Points:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Deployment (Docker Swarm)

```bash
# Configure environment
cp .env.production.example .env.production
nano .env.production

# Deploy to swarm
./scripts/deploy.sh deploy --build
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production setup.

## 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React 18 + TypeScript + Tailwind CSS | Modern, responsive UI |
| **Backend** | FastAPI + SQLAlchemy + PostgreSQL | High-performance API |
| **Jobs** | Celery + Redis | Background processing |
| **Auth** | Steam OpenID + JWT | Secure authentication |
| **Deploy** | Docker + Docker Swarm | Container orchestration |
| **CI/CD** | GitHub Actions | Automated testing & deployment |

## 📊 Detection System

StatSentry uses a sophisticated scoring algorithm to identify suspicious players:

### Detection Criteria
- 🆕 **New Account Analysis** - Recent account creation with high performance
- 🔒 **Private Profile Flags** - Private profiles with suspicious stats
- ⚠️ **VAC History** - Previous VAC bans in other games
- 🎮 **Playtime Anomalies** - CS2-only accounts with limited game libraries
- 📈 **Performance Spikes** - Sudden improvement in gameplay metrics
- 🎯 **Statistical Analysis** - Unnatural consistency patterns

### Scoring System
- **0-30**: Unlikely to cheat
- **31-60**: Suspicious patterns detected
- **61-80**: Highly suspicious behavior
- **81-100**: Almost certainly cheating

## 📁 Project Structure

```
statsentry/
├── 🔙 backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/             # REST API endpoints
│   │   ├── core/            # Configuration & security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── tasks/           # Celery background tasks
│   ├── alembic/             # Database migrations
│   └── tests/               # Backend tests
├── 🎨 frontend/             # React frontend
│   └── src/
│       ├── components/      # Reusable UI components
│       ├── pages/           # Application pages
│       ├── services/        # API integration
│       └── types/           # TypeScript definitions
├── 📚 docs/                 # Documentation
├── 🛠️ scripts/              # Deployment & utility scripts
├── 🐳 .github/              # GitHub Actions workflows
└── 📋 docker-compose*.yml   # Docker configurations
```

## ⚙️ Configuration

### Required Environment Variables

```bash
# Steam API (get from https://steamcommunity.com/dev/apikey)
STEAM_API_KEY=your_steam_api_key_here

# Security
SECRET_KEY=your_super_secure_jwt_secret_key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/statsentry

# Optional: Leetify API Integration
LEETIFY_API_KEY=your_leetify_api_key_here
```

See [SETUP.md](docs/SETUP.md) for complete configuration guide.

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

StatSentry is designed for educational and analytical purposes. It only accesses publicly available Steam profile data and does not interact with CS2 game files or memory. Always follow Steam's Terms of Service and use responsibly.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/yourusername/statsentry/issues)
- 💬 [Discussions](https://github.com/yourusername/statsentry/discussions)

---

**Made with ❤️ for the CS2 community**