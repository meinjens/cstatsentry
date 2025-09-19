#!/bin/bash

echo "🚀 Initializing StatSentry Git Repository"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: StatSentry CS2 Anti-Cheat Detection System

Features:
- Steam OAuth authentication
- Player profile analysis and scoring
- VAC/Game ban detection
- FastAPI backend with PostgreSQL
- React frontend with TypeScript
- Celery background job processing
- Docker Swarm deployment ready
- Complete CI/CD pipeline

🛡️ CS2 Anti-Cheat Detection System
🎯 Automated teammate analysis
🔍 Suspicious player identification
🚀 Production-ready deployment"

echo "✅ Repository initialized with initial commit"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Add the remote origin:"
echo "   git remote add origin https://github.com/yourusername/statsentry.git"
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📁 Repository structure:"
echo "├── backend/          # FastAPI backend"
echo "├── frontend/         # React frontend"
echo "├── docs/            # Documentation"
echo "├── scripts/         # Deployment scripts"
echo "├── .github/         # GitHub workflows"
echo "└── docker-compose.* # Docker configurations"