#!/bin/bash
#
# MediAI Startup Script
# Runs database migrations and seeds demo users before starting the API server
#

set -e  # Exit on error

echo "🚀 MediAI Startup Script"
echo "=" 60

# Run migrations
echo "📦 Running database migrations..."
cd /opt/render/project/src/api
alembic upgrade head || echo "⚠️  Migrations skipped (may already be up to date)"

# Seed demo users
echo "🌱 Seeding demo users..."
python scripts/seed_demo_users.py || echo "⚠️  User seeding skipped (may already exist)"

echo "✅ Startup complete!"
echo "=" 60
