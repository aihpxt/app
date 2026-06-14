@echo off
chcp 65001 >nul
cd /d d:\aiphxt-app\ai-service
call venv\Scripts\activate.bat
python test_app_startup.py 2>&1
