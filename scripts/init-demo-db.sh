#!/bin/bash
# Initialize the demo service database

set -e

echo "🎯 Initializing Demo Service Database..."

# Wait for PostgreSQL to be ready
until docker-compose exec -T db pg_isready -U statsentry; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Create csdemos database if it doesn't exist
docker-compose exec -T db psql -U statsentry -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'csdemos'" | grep -q 1 || \
  docker-compose exec -T db psql -U statsentry -d postgres -c "CREATE DATABASE csdemos;"

echo "✅ Database 'csdemos' ready"

# Run Prisma migrations
echo "🔄 Running Prisma migrations..."
docker-compose exec -T demo-service pnpm prisma:migrate

echo "✅ Demo Service Database initialized successfully!"
