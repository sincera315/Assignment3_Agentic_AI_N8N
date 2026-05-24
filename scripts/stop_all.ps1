# Phase 7 Integration & Testing
# Shutdown Script for All Services

Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "  AIRSPACE COPILOT - SYSTEM SHUTDOWN"
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""

$ErrorActionPreference = "Stop"

Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
Write-Host ""

try {
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All services stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to stop services" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error stopping services: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "💤 System shutdown complete" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start again, run: .\scripts\start_all.ps1" -ForegroundColor Cyan
Write-Host ""
