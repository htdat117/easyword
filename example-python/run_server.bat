@echo off
echo Starting EasyWord FastAPI Server...
cd /d "%~dp0"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
pause
