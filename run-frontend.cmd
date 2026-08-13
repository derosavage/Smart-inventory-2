@echo off
cd /d "%~dp0"
call venv\Scripts\python.exe -m http.server 8080
