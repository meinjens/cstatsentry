#!/bin/bash

# Production Deployment Script for CStatSentry
set -e

echo "🚀 Starting CStatSentry Production Deployment"

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: .env.prod file not found!"
    echo "Please create .env.prod with your production environment variables:"
    echo "  POSTGRES_PASSWORD=your_secure_password"
    echo "  SECRET_KEY=your_secure_secret_key"
    echo "  STEAM_API_KEY=your_steam_api_key"
    echo "  FRONTEND_URL=https://your-domain.com"
    exit 1
fi

# Load environment variables
export $(cat .env.prod | grep -v '^#' | xargs)

echo "📋 Environment loaded from .env.prod"

# Build images
echo "🔨 Building Docker images..."
docker build -t cstatsentry/backend-service:latest ./backend
docker build -t cstatsentry/frontend:latest ./frontend

echo "🗄️  Starting database and Redis..."
docker compose -f docker-compose.prod.yml up -d db redis

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🔄 Running database migrations..."
docker compose -f docker-compose.prod.yml up migration

echo "🚀 Starting all services..."
docker compose -f docker-compose.prod.yml up -d

echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: ${FRONTEND_URL:-http://localhost}"
echo "📊 API health check: curl ${FRONTEND_URL:-http://localhost}/api/v1/health"

echo ""
echo "📝 To check logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f api"
echo ""
echo "🔍 To check migration status:"
echo "  docker compose -f docker-compose.prod.yml exec api alembic current"