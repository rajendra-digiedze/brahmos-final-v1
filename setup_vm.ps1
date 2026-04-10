Write-Host "Setting up the fresh Windows VM for the Cyber Security 7-Layer Architecture project..."

# Check if winget is available
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing Docker Desktop using winget..."
    winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    
    Write-Host "Installing Python (optional, for local debugging outside docker)..."
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements

    Write-Host "Installing Node.js (optional, for local frontend UI dev outside docker)..."
    winget install -e --id OpenJS.NodeJS --accept-package-agreements --accept-source-agreements
} else {
    Write-Warning "winget is not available. Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop/"
}

Write-Host ""
Write-Host "========================================================================="
Write-Host "IMPORTANT: Please reboot your VM and then open 'Docker Desktop' manually."
Write-Host "Once Docker Engine is running, open a terminal in this folder and run:"
Write-Host "  docker compose up --build"
Write-Host "========================================================================="
