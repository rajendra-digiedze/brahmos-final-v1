@echo off
echo ========================================================
echo dZshield/Brahmos SOC Project - Dependency Installer
echo ========================================================
echo.
echo This script will install Python, Node.js, and all project 
echo dependencies for the backend, frontend, and log generator.
echo.
pause

echo.
echo [1/4] Installing System Tools (Python, Node.js) via Winget
echo --------------------------------------------------------
echo Starting install for Python 3.11...
winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
echo Starting install for Node.js...
winget install -e --id OpenJS.NodeJS --accept-package-agreements --accept-source-agreements

echo.
echo [2/4] Installing Backend Dependencies (Python)
echo --------------------------------------------------------
cd /d "%~dp0backend"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [3/4] Installing Log Generator Dependencies (Python)
echo --------------------------------------------------------
cd /d "%~dp0log_generator"
pip install -r requirements.txt

echo.
echo [4/4] Installing Frontend Dependencies (Node.js React)
echo --------------------------------------------------------
cd /d "%~dp0frontend"
call npm install

echo.
echo ========================================================
echo Installation completed successfully!
echo You can now run "start_dashboard.bat" to start the SOC.
echo ========================================================
pause
