# Update Model Configuration
Write-Host "🔧 Updating Groq Model Configuration..." -ForegroundColor Cyan
Write-Host ""
Write-Host "The model llama3-70b-8192 has been decommissioned by Groq." -ForegroundColor Yellow
Write-Host "Updating to: llama-3.1-70b-versatile" -ForegroundColor Green
Write-Host ""

# Update .env file if it exists
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    # Replace all old model variants with the new one
    $envContent = $envContent -replace 'AGENT_MODEL=llama3-70b-8192', 'AGENT_MODEL=llama-3.1-70b-versatile'
    $envContent = $envContent -replace 'AGENT_MODEL=llama3-70b-versatile', 'AGENT_MODEL=llama-3.1-70b-versatile'
    $envContent | Set-Content ".env" -NoNewline
    Write-Host "✅ Updated .env file" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found - creating from .env.example" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file" -ForegroundColor Green
        Write-Host "⚠️  Please update GROQ_API_KEY in .env" -ForegroundColor Magenta
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📝 Updated Model:" -ForegroundColor Cyan
Write-Host "   Old: llama3-70b-8192 (decommissioned)" -ForegroundColor Red
Write-Host "   New: llama-3.1-70b-versatile ✅" -ForegroundColor Green
Write-Host ""
Write-Host "Now run: python test_agents.py" -ForegroundColor Yellow
