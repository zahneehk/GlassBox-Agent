#!/bin/bash
# Quick setup for GlassBox dev environment
set -e

echo "=== GlassBox-Agent Dev Setup ==="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Please install Docker first."
    exit 1
fi

# Check docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: docker-compose not found."
    exit 1
fi

echo "[1/3] Starting infrastructure (postgres, redis)..."
cd infra/compose
docker compose -f docker-compose.dev.yml up -d postgres redis
sleep 3

echo "[2/3] Building orchestrator..."
docker compose -f docker-compose.dev.yml build orchestrator

echo "[3/3] Starting orchestrator + nginx..."
docker compose -f docker-compose.dev.yml up -d

echo ""
echo "=== GlassBox-Agent is running ==="
echo "  Orchestrator: http://localhost:8000/health"
echo "  Web UI:       http://localhost:80"
echo "  PostgreSQL:   localhost:5432"
echo "  Redis:        localhost:6379"
