#!/bin/bash

set -e

echo "🚀 StatSentry Docker Swarm Deployment Script"

# Configuration
REGISTRY=${REGISTRY:-"your-registry.com"}
VERSION=${VERSION:-"latest"}
STACK_NAME=${STACK_NAME:-"cstatsentry"}

# Build and push images
build_and_push() {
    echo "🔨 Building and pushing Docker images..."

    # Build API image
    echo "Building API image..."
    docker build -t ${REGISTRY}/statsentry/api:${VERSION} ./backend
    docker push ${REGISTRY}/statsentry/api:${VERSION}

    # Build Frontend image
    echo "Building Frontend image..."
    docker build -t ${REGISTRY}/statsentry/frontend:${VERSION} ./frontend
    docker push ${REGISTRY}/statsentry/frontend:${VERSION}

    echo "✅ Images built and pushed successfully!"
}

# Initialize Docker Swarm (if not already initialized)
init_swarm() {
    if ! docker info | grep -q "Swarm: active"; then
        echo "🐳 Initializing Docker Swarm..."
        docker swarm init
    else
        echo "✅ Docker Swarm already active"
    fi
}

# Create network
create_network() {
    if ! docker network ls | grep -q "statsentry-network"; then
        echo "🌐 Creating overlay network..."
        docker network create --driver overlay --attachable statsentry-network
    else
        echo "✅ Network already exists"
    fi
}

# Deploy stack
deploy_stack() {
    echo "🚀 Deploying StatSentry stack..."

    # Check if .env.production exists
    if [ ! -f .env.production ]; then
        echo "❌ .env.production file not found!"
        echo "Please copy .env.production.example to .env.production and configure it."
        exit 1
    fi

    # Load environment variables
    export $(grep -v '^#' .env.production | xargs)

    # Update image tags in compose file
    sed -i.bak "s|statsentry/api:latest|${REGISTRY}/statsentry/api:${VERSION}|g" docker-compose.prod.yml
    sed -i.bak "s|statsentry/frontend:latest|${REGISTRY}/statsentry/frontend:${VERSION}|g" docker-compose.prod.yml

    # Deploy stack
    docker stack deploy -c docker-compose.prod.yml ${STACK_NAME}

    # Restore original compose file
    mv docker-compose.prod.yml.bak docker-compose.prod.yml

    echo "✅ Stack deployed successfully!"
}

# Run database migrations
run_migrations() {
    echo "🗄️ Running database migrations..."

    # Wait for API service to be ready
    echo "Waiting for API service to be ready..."
    sleep 30

    # Get API container ID
    API_CONTAINER=$(docker ps --filter "name=${STACK_NAME}_api" --format "{{.ID}}" | head -n1)

    if [ -n "$API_CONTAINER" ]; then
        echo "Running migrations in container: $API_CONTAINER"
        docker exec $API_CONTAINER alembic upgrade head
        echo "✅ Migrations completed!"
    else
        echo "⚠️ Could not find API container. Please run migrations manually:"
        echo "docker exec \$(docker ps --filter \"name=${STACK_NAME}_api\" --format \"{{.ID}}\" | head -n1) alembic upgrade head"
    fi
}

# Show stack status
show_status() {
    echo "📊 Stack Status:"
    docker stack services ${STACK_NAME}
    echo ""
    echo "📝 Service Logs (use these commands to check logs):"
    echo "docker service logs ${STACK_NAME}_api"
    echo "docker service logs ${STACK_NAME}_frontend"
    echo "docker service logs ${STACK_NAME}_celery-worker"
    echo "docker service logs ${STACK_NAME}_nginx"
}

# Main deployment function
deploy() {
    echo "Starting deployment process..."

    init_swarm
    create_network

    if [ "$1" = "--build" ]; then
        build_and_push
    fi

    deploy_stack
    run_migrations
    show_status

    echo ""
    echo "🎉 StatSentry deployment complete!"
    echo "Access your application at: http://your-domain.com"
    echo ""
    echo "To update the application:"
    echo "./scripts/deploy.sh --build"
    echo ""
    echo "To remove the stack:"
    echo "docker stack rm ${STACK_NAME}"
}

# Handle command line arguments
case "$1" in
    "build")
        build_and_push
        ;;
    "deploy")
        deploy
        ;;
    "status")
        show_status
        ;;
    "logs")
        if [ -n "$2" ]; then
            docker service logs ${STACK_NAME}_$2
        else
            echo "Usage: $0 logs <service_name>"
            echo "Available services: api, frontend, celery-worker, celery-beat, nginx, db, redis"
        fi
        ;;
    "remove")
        echo "🗑️ Removing StatSentry stack..."
        docker stack rm ${STACK_NAME}
        echo "✅ Stack removed!"
        ;;
    *)
        echo "Usage: $0 {deploy|build|status|logs|remove} [options]"
        echo ""
        echo "Commands:"
        echo "  deploy [--build]  Deploy the application (optionally build images first)"
        echo "  build            Build and push Docker images"
        echo "  status           Show stack status"
        echo "  logs <service>   Show logs for a specific service"
        echo "  remove           Remove the entire stack"
        echo ""
        echo "Environment variables:"
        echo "  REGISTRY         Docker registry URL (default: your-registry.com)"
        echo "  VERSION          Image version tag (default: latest)"
        echo "  STACK_NAME       Docker stack name (default: statsentry)"
        exit 1
        ;;
esac