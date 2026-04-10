Write-Host "Attempting to start Docker Desktop..."
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue

Write-Host "Waiting for Docker Daemon to boot... (this might take up to 60 seconds)"
$dockerReady = $false
for ($i = 0; $i -lt 30; $i++) {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
        break
    }
    Write-Host "Waiting..."
    Start-Sleep -Seconds 5
}

if ($dockerReady) {
    Write-Host "Docker is ready! Launching all services..."
    Set-Location -Path "c:\Users\r6304076576\Downloads\brahmos"
    docker-compose down
    docker-compose up -d --build
    
    Write-Host "All services have been started in Docker successfully!"
    Write-Host "Please allow 30 seconds for all containers to fully boot their web interfaces."
    Write-Host "L7 Web Dashboard: http://localhost:5173"
    Write-Host "L6 n8n Orchestrator: http://localhost:5678"
    Write-Host "L4/L5 AI / LangGraph Backend API: http://localhost:8000/docs"
    Write-Host "L3 Qdrant Vector DB: http://localhost:6333/dashboard"
} else {
    Write-Host "Docker failed to start. Please open 'Docker Desktop' manually from your Windows Start menu."
}
