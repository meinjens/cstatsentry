# StatSentry Setup Guide

This guide will help you set up StatSentry for development and production.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (recommended)

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required - Get from Steam Developer portal
STEAM_API_KEY=your_steam_api_key_here

# Required - Generate a secure secret key
SECRET_KEY=your-super-secret-jwt-key-here

# Optional - Leetify API integration
LEETIFY_API_KEY=your_leetify_api_key_here

# Database URLs (defaults work for Docker setup)
DATABASE_URL=postgresql://statsentry:password@localhost:5432/statsentry
REDIS_URL=redis://localhost:6379/0
```

## Getting Steam API Key

1. Go to https://steamcommunity.com/dev/apikey
2. Enter your domain name (or localhost for development)
3. Copy the generated API key to your `.env` file

## Quick Start with Docker

1. **Clone and setup environment:**
   ```bash
   git clone <repository>
   cd cstatsentry
   cp .env.example .env
   # Edit .env with your Steam API key
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations:**
   ```bash
   cd backend
   docker-compose exec api alembic upgrade head
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   # Start PostgreSQL and Redis
   createdb statsentry

   # Run migrations
   alembic upgrade head
   ```

3. **Start the API server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Celery worker (separate terminal):**
   ```bash
   celery -A app.core.celery worker --loglevel=info
   ```

5. **Start Celery beat scheduler (separate terminal):**
   ```bash
   celery -A app.core.celery beat --loglevel=info
   ```

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000

## Development Workflow

### Database Changes

1. **Modify models** in `backend/app/models/`
2. **Generate migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   ```
3. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

### Adding API Endpoints

1. **Add endpoint** in `backend/app/api/api_v1/endpoints/`
2. **Include router** in `backend/app/api/api_v1/api.py`
3. **Update frontend API service** in `frontend/src/services/api.ts`

### Adding Frontend Pages

1. **Create page component** in `frontend/src/pages/`
2. **Add route** in `frontend/src/App.tsx`
3. **Update navigation** in `frontend/src/components/Layout.tsx`

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Production Deployment

### Environment Setup

1. **Set production environment variables:**
   ```bash
   DEBUG=false
   DATABASE_URL=postgresql://user:pass@prod-db:5432/statsentry
   REDIS_URL=redis://prod-redis:6379/0
   FRONTEND_URL=https://your-domain.com
   ```

2. **Use production-ready secrets:**
   - Generate a strong `SECRET_KEY`
   - Use environment-specific API keys
   - Configure secure database credentials

### Docker Production

1. **Build images:**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Manual Production

1. **Configure reverse proxy** (Nginx recommended)
2. **Use process manager** (systemd, supervisor, or PM2)
3. **Set up SSL certificates** (Let's Encrypt recommended)
4. **Configure monitoring** and logging

## Troubleshooting

### Common Issues

1. **Steam API Key Invalid:**
   - Verify key is correct in `.env`
   - Check Steam Developer portal for domain restrictions

2. **Database Connection Failed:**
   - Ensure PostgreSQL is running
   - Check `DATABASE_URL` in `.env`
   - Verify database exists and user has permissions

3. **Redis Connection Failed:**
   - Ensure Redis is running
   - Check `REDIS_URL` in `.env`

4. **Celery Tasks Not Running:**
   - Ensure Redis is running (used as message broker)
   - Check Celery worker and beat are started
   - Verify `CELERY_BROKER_URL` is correct

### Logs

- **API logs:** Check Docker logs or console output
- **Celery logs:** Check worker/beat console output
- **Frontend logs:** Check browser console
- **Database logs:** Check PostgreSQL logs

### Health Checks

- **API Health:** `curl http://localhost:8000/health`
- **Database:** Check if migrations applied successfully
- **Redis:** `redis-cli ping`
- **Frontend:** Check if app loads at http://localhost:3000

## Performance Optimization

### Database

- Monitor query performance with `EXPLAIN ANALYZE`
- Add indexes for frequently queried columns
- Consider connection pooling for high load

### API

- Enable API response caching for read-heavy endpoints
- Use background tasks for heavy operations
- Monitor API response times

### Frontend

- Implement proper error boundaries
- Use React Query for efficient data fetching
- Optimize bundle size with code splitting

### Background Jobs

- Monitor Celery queue sizes
- Scale workers based on load
- Use appropriate task priorities