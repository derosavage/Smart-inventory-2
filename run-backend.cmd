@echo off
set PORT=8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
  echo Backend already appears to be running on http://127.0.0.1:%PORT%
  pause
  exit /b 0
)
cd /d "%~dp0backend"
call ..\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port %PORT%
pause
