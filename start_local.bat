@echo off
chcp 65001 >nul
echo ====================================
echo   小龙虾择校系统 - 本地部署启动
echo ====================================
echo.

echo [1/3] 启动Redis缓存服务...
redis-server --service-start
timeout /t 1 >nul

echo [2/3] 启动AI后端服务...
cd /d "d:\aiphxt-app\ai-service"
start "AI Service" cmd /k "d:\aiphxt-app\ai-service\venv\Scripts\python.exe -m uvicorn app.core.app:app --host 0.0.0.0 --port 8001"
timeout /t 3 >nul

echo [3/3] 启动前端服务...
cd /d "d:\aiphxt-app\frontend\dist"
start "Frontend" cmd /k "C:\Users\小葱花\AppData\Local\Programs\Python\Python311\python.exe -m http.server 3000"

echo.
echo ====================================
echo   服务启动完成！
echo ====================================
echo.
echo   前端地址: http://localhost:3000
echo   后端API:  http://localhost:8001
echo   API文档:  http://localhost:8001/docs
echo   Redis:    localhost:6379
echo.
echo   按任意键退出此窗口...
pause >nul