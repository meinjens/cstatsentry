#!/bin/bash

set -e

echo "🧪 Testing CI Pipeline Steps"
echo "===================================="

echo ""
echo "📦 Frontend Tests:"
echo "-------------------"

# Frontend Lint
echo "1. Running frontend linting..."
cd frontend
pnpm run lint
echo "✅ Frontend lint passed"

# Frontend Tests
echo "2. Running frontend tests..."
pnpm test
echo "✅ Frontend tests passed"

# Frontend Build
echo "3. Building frontend..."
pnpm run build
echo "✅ Frontend build passed"

cd ..

echo ""
echo "🐳 Backend Tests (Docker):"
echo "---------------------------"

# Backend Tests with PostgreSQL and Redis
echo "4. Running backend tests with coverage..."
docker compose -f docker-compose.test.yml down --remove-orphans --volumes
docker compose -f docker-compose.test.yml up --build backend-test --abort-on-container-exit
echo "✅ Backend tests passed"

echo ""
echo "🏗️ Docker Builds:"
echo "-------------------"

# Docker builds
echo "5. Building Docker images..."
docker build -t cstatsentry/api:test ./backend
docker build -t cstatsentry/frontend:test ./frontend
echo "✅ Docker builds passed"

echo ""
echo "🎉 All CI Pipeline Steps Completed Successfully!"
echo "================================================"
echo ""
echo "Summary:"
echo "✅ Frontend linting"
echo "✅ Frontend tests"
echo "✅ Frontend build"
echo "✅ Backend tests with coverage"
echo "✅ Docker image builds"