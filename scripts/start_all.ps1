# Phase 7 Integration & Testing - Complete Implementation
# Startup Script for All Services

Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "  AIRSPACE COPILOT - SYSTEM STARTUP"
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""

$ErrorActionPreference = "Stop"

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Cyan

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found." -ForegroundColor Red
    exit 1
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please create it from .env.example" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

Write-Host ""

# Start services
Write-Host "🚀 Starting all services with Docker Compose..." -ForegroundColor Cyan
Write-Host ""

try {
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All services started successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error starting services: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""

# Check service status
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host ""
docker-compose ps

Write-Host ""

# Display access URLs
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "  ACCESS URLS"
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""
Write-Host "  🌐 n8n Workflows:    http://localhost:5678" -ForegroundColor Green
Write-Host "  🔧 MCP Server:       http://localhost:8000" -ForegroundColor Green
Write-Host "  ✈️  Streamlit UI:     http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "  📊 Health Check:     http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "  📚 API Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""

# Run health check
Write-Host "🏥 Running health check..." -ForegroundColor Cyan
Write-Host ""

try {
    python monitoring/health_checker.py
} catch {
    Write-Host "⚠️  Health check script not available. Services may still be starting..." -ForegroundColor Yellow
}

Write-Host ""

# Next steps
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "  NEXT STEPS"
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""
Write-Host "  1. Open n8n at http://localhost:5678" -ForegroundColor White
Write-Host "     - Import workflows from n8n_workflows/ directory" -ForegroundColor Gray
Write-Host "     - Activate all 3 region workflows" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Open Streamlit UI at http://localhost:8501" -ForegroundColor White
Write-Host "     - Test Traveler Mode (track a flight)" -ForegroundColor Gray
Write-Host "     - Test Operations Mode (analyze a region)" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Run integration tests:" -ForegroundColor White
Write-Host "     pytest tests/test_integration.py -v" -ForegroundColor Gray
Write-Host ""
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""

Write-Host "✨ System startup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To stop all services, run: .\scripts\stop_all.ps1" -ForegroundColor Cyan
Write-Host ""
