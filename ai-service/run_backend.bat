@echo off
cd /d D:\aiphxt-app\ai-service
python -m uvicorn app.core.app:app --host 0.0.0.0 --port 8000
pause
