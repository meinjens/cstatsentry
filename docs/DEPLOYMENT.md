# StatSentry Docker Swarm Deployment Guide

## Overview

StatSentry is designed for production deployment using Docker Swarm with the following architecture:

- **2x API replicas** (FastAPI backend)
- **2x Frontend replicas** (React SPA)
- **2x Celery workers** (Background job processing)
- **1x Celery beat scheduler** (Task scheduling)
- **1x PostgreSQL database** (Persistent storage)
- **1x Redis** (Cache and message broker)
- **1x Nginx** (Load balancer and reverse proxy)

## Prerequisites

- Docker Swarm cluster initialized
- Domain name configured (for production)
- SSL certificates (for HTTPS)
- Docker registry access (for image storage)

## Quick Deployment

### 1. Environment Setup

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with your configuration
nano .env.production
```

Required configuration:
```bash
# Database
POSTGRES_PASSWORD=your_secure_database_password
STEAM_API_KEY=your_steam_api_key
SECRET_KEY=your_super_secure_jwt_secret_key
FRONTEND_URL=https://your-domain.com
```

### 2. Deploy to Swarm

```bash
# Build images and deploy
./scripts/deploy.sh deploy --build

# Or deploy with existing images
./scripts/deploy.sh deploy
```

### 3. Check Status

```bash
# View service status
./scripts/deploy.sh status

# Check logs
./scripts/deploy.sh logs api
./scripts/deploy.sh logs frontend
```

## Manual Deployment Steps

### 1. Initialize Swarm

```bash
# On manager node
docker swarm init

# On worker nodes (get token from manager)
docker swarm join --token <token> <manager-ip>:2377
```

### 2. Create Network

```bash
docker network create --driver overlay --attachable statsentry-network
```

### 3. Build and Push Images

```bash
# Set your registry
export REGISTRY="your-registry.com"
export VERSION="v1.0.0"

# Build API image
docker build -t ${REGISTRY}/statsentry/api:${VERSION} ./backend
docker push ${REGISTRY}/statsentry/api:${VERSION}

# Build Frontend image
docker build -t ${REGISTRY}/statsentry/frontend:${VERSION} ./frontend
docker push ${REGISTRY}/statsentry/frontend:${VERSION}
```

### 4. Deploy Stack

```bash
# Load environment variables
export $(grep -v '^#' .env.production | xargs)

# Deploy stack
docker stack deploy -c docker-compose.prod.yml statsentry
```

### 5. Run Database Migrations

```bash
# Get API container ID
API_CONTAINER=$(docker ps --filter "name=statsentry_api" --format "{{.ID}}" | head -n1)

# Run migrations
docker exec $API_CONTAINER alembic upgrade head
```

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_DB` | Database name | No | `statsentry` |
| `POSTGRES_USER` | Database user | No | `statsentry` |
| `POSTGRES_PASSWORD` | Database password | Yes | - |
| `STEAM_API_KEY` | Steam Web API key | Yes | - |
| `SECRET_KEY` | JWT signing key | Yes | - |
| `FRONTEND_URL` | Frontend domain URL | No | `https://statsentry.your-domain.com` |
| `LEETIFY_API_KEY` | Leetify API key | No | - |

### Resource Limits

Default resource limits in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Scaling Services

```bash
# Scale API service
docker service scale statsentry_api=4

# Scale Celery workers
docker service scale statsentry_celery-worker=4

# Scale frontend
docker service scale statsentry_frontend=3
```

## SSL/HTTPS Configuration

### 1. Obtain SSL Certificates

```bash
# Using Let's Encrypt (example)
certbot certonly --webroot -w /var/www/html -d your-domain.com
```

### 2. Update Nginx Configuration

Edit `nginx.conf` to enable HTTPS:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Include same location blocks as HTTP server
}
```

### 3. Mount SSL Certificates

Add to `docker-compose.prod.yml`:

```yaml
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl:ro
```

## Monitoring and Logging

### Service Logs

```bash
# View logs for specific service
docker service logs statsentry_api
docker service logs statsentry_frontend
docker service logs statsentry_celery-worker

# Follow logs in real-time
docker service logs -f statsentry_api
```

### Health Checks

All services include health checks:

- **API**: `GET /health`
- **Frontend**: `GET /health`
- **Database**: `pg_isready`
- **Redis**: `redis-cli ping`

### Monitoring Stack Status

```bash
# List all services
docker stack services statsentry

# Check service details
docker service inspect statsentry_api

# View service tasks
docker service ps statsentry_api
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker exec $(docker ps --filter "name=statsentry_db" --format "{{.ID}}" | head -n1) \
  pg_dump -U statsentry statsentry > backup-$(date +%Y%m%d).sql

# Restore backup
docker exec -i $(docker ps --filter "name=statsentry_db" --format "{{.ID}}" | head -n1) \
  psql -U statsentry statsentry < backup-20231201.sql
```

### Volume Backup

```bash
# Backup PostgreSQL data
docker run --rm -v statsentry_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore PostgreSQL data
docker run --rm -v statsentry_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup-20231201.tar.gz -C /data
```

## Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check service logs
   docker service logs statsentry_api

   # Check node resources
   docker node ls
   ```

2. **Database connection issues**
   ```bash
   # Check database service
   docker service ps statsentry_db

   # Test connection
   docker exec -it $(docker ps --filter "name=statsentry_db" -q) psql -U statsentry
   ```

3. **Image pull failures**
   ```bash
   # Check registry authentication
   docker login your-registry.com

   # Manually pull image
   docker pull your-registry.com/statsentry/api:latest
   ```

### Rolling Updates

```bash
# Update API service
docker service update --image your-registry.com/statsentry/api:v1.1.0 statsentry_api

# Update with zero downtime
docker service update --update-parallelism 1 --update-delay 30s \
  --image your-registry.com/statsentry/api:v1.1.0 statsentry_api
```

### Rollback

```bash
# Rollback to previous version
docker service rollback statsentry_api

# Check rollback status
docker service ps statsentry_api
```

## Security Considerations

1. **Secrets Management**
   - Use Docker secrets for sensitive data
   - Rotate secrets regularly
   - Never commit secrets to Git

2. **Network Security**
   - Use overlay networks for service communication
   - Implement proper firewall rules
   - Consider using Docker secrets

3. **Container Security**
   - Run containers as non-root users
   - Keep base images updated
   - Scan images for vulnerabilities

4. **SSL/TLS**
   - Use strong SSL ciphers
   - Implement HSTS headers
   - Use HTTP/2 for better performance

## Performance Tuning

### Database Optimization

```bash
# Increase PostgreSQL connections
docker service update --env-add POSTGRES_MAX_CONNECTIONS=200 statsentry_db
```

### API Optimization

```bash
# Increase API workers
docker service update --env-add WORKERS=8 statsentry_api
```

### Celery Optimization

```bash
# Increase Celery concurrency
docker service update --env-add CELERY_CONCURRENCY=8 statsentry_celery-worker
```

## Support

For deployment issues:

1. Check service logs: `./scripts/deploy.sh logs <service>`
2. Verify configuration: `./scripts/deploy.sh status`
3. Review Docker Swarm documentation
4. Check GitHub issues for known problems