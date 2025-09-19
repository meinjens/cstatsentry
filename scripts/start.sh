#!/bin/bash

echo "🚀 Starting StatSentry Development Environment"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your configuration"
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d db redis

# Wait for services to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "📦 Installing Python dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate

    # Add PostgreSQL to PATH for macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
        pip install -r requirements-macos.txt
    else
        pip install -r requirements.txt
    fi
    cd ..
fi

# Run database migrations
echo "🗄️ Running database migrations..."
cd backend
source venv/bin/activate
alembic upgrade head
cd ..

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "✅ StatSentry is ready!"
echo ""
echo "📋 Next steps:"
echo "1. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. Start Celery worker (new terminal):"
echo "   cd backend && source venv/bin/activate && celery -A app.core.celery worker --loglevel=info"
echo ""
echo "3. Start Celery beat (new terminal):"
echo "   cd backend && source venv/bin/activate && celery -A app.core.celery beat --loglevel=info"
echo ""
echo "4. Start the frontend (new terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"