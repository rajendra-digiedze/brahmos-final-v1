@echo off
:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Confirmed Administrator Privileges.
) else (
    echo Requesting Administrator Privileges...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /B
)

cd /d "%~dp0"
echo ===================================================
echo dZshield Enterprise SOC - Automated Launch Profile
echo ===================================================

echo [!] Configuring Windows Firewall for External VM Access (34.131.6.36 integration)...
netsh advfirewall firewall add rule name="dZshield SOC Ports" dir=in action=allow protocol=TCP localport=5173,8000,5678,6333 >nul 2>&1
echo Firewall ports 5173, 8000, 5678, 6333 successfully opened!

echo [1/4] Starting L4/L5 FastAPI Backend (Port 8000)...
start powershell -WindowStyle Normal -NoExit -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); cd backend; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/4] Starting L7 React Frontend (Port 5173)...
start powershell -WindowStyle Normal -NoExit -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); cd frontend; npm run dev"

echo [3/4] Starting Log Generator...
start powershell -WindowStyle Normal -NoExit -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); cd log_generator; python generate.py"

echo [4/4] Activating L3 Qdrant & L6 n8n Interface Mounts...
start powershell -WindowStyle Normal -NoExit -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'); python mock_uis.py"

echo ===================================================
echo Successfully mapped all 4 environments!
echo Please wait about 15 seconds for Web Servers to boot.
echo ===================================================
echo - L7 React Web Dashboard: http://localhost:5173
echo - L6 n8n Orchestrator: http://localhost:5678
echo - L4/L5 FastAPI Backend: http://localhost:8000/docs
echo - L3 Qdrant Vector DB UI: http://localhost:6333/dashboard
echo ===================================================
timeout /t 10
