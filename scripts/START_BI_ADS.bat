@echo off
echo ========================================
echo   BI ADS - MULTI TOOL PRO v2.0
echo   Starting Backend + Frontend...
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

REM Install Python dependencies
echo [1/4] Installing Python dependencies...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

REM Install Node dependencies
echo.
echo [2/4] Installing Node.js dependencies...
call npm install

REM Start backend in background
echo.
echo [3/4] Starting Backend API on http://localhost:8000...
start "Bi Ads Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo.
echo [4/4] Starting Electron Frontend...
start "Bi Ads Frontend" cmd /k "npm start"

echo.
echo ========================================
echo   BI ADS MULTI TOOL PRO STARTED!
echo ========================================
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Press any key to stop all services...
pause >nul

REM Kill processes
taskkill /F /FI "WindowTitle eq Bi Ads Backend*" >nul 2>nul
taskkill /F /FI "WindowTitle eq Bi Ads Frontend*" >nul 2>nul

echo.
echo All services stopped.
pause
