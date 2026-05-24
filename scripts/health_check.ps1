# Phase 7 Integration & Testing
# Quick Health Check Script

Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "  SYSTEM HEALTH CHECK"
Write-Host "=" -NoNewline; for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""

$services = @(
    @{Name="n8n"; URL="http://localhost:5678"; Port=5678},
    @{Name="MCP Server"; URL="http://localhost:8000/health"; Port=8000},
    @{Name="Streamlit UI"; URL="http://localhost:8501"; Port=8501}
)

foreach ($service in $services) {
    Write-Host "🔍 Checking $($service.Name)..." -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host " 🟢 Online" -ForegroundColor Green
        } else {
            Write-Host " 🔴 Error (HTTP $($response.StatusCode))" -ForegroundColor Red
        }
    } catch {
        Write-Host " 🔴 Offline" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 Docker Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""

# Check data files
Write-Host "📁 Data Pipeline Status:" -ForegroundColor Cyan
$regions = @("region1", "region2", "region3")

foreach ($region in $regions) {
    $file = "data/flight_snapshots/${region}_latest.json"
    if (Test-Path $file) {
        $age = (Get-Date) - (Get-Item $file).LastWriteTime
        Write-Host "   $region : 🟢 Active (${age.TotalSeconds:N0}s old)" -ForegroundColor Green
    } else {
        Write-Host "   $region : 🔴 Missing" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "For detailed health report, run:" -ForegroundColor Cyan
Write-Host "  python monitoring/health_checker.py" -ForegroundColor White
Write-Host ""
