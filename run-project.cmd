@echo off
setlocal
set BACKEND_PORT=8000
set FRONTEND_PORT=8080

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%BACKEND_PORT% ^| findstr LISTENING') do set BACKEND_RUNNING=1
if not defined BACKEND_RUNNING start "Smart Inventory Backend" "%~dp0run-backend.cmd"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%FRONTEND_PORT% ^| findstr LISTENING') do set FRONTEND_RUNNING=1
if not defined FRONTEND_RUNNING start "Smart Inventory Frontend" "%~dp0run-frontend.cmd"

timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:%FRONTEND_PORT%/index.html"
start "" "http://127.0.0.1:%FRONTEND_PORT%/login.html"
endlocal
