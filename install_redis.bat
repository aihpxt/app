@echo off
chcp 65001 >nul
echo ====================================
echo   Redis 安装脚本
echo ====================================
echo.

echo 1. 下载 Redis 安装包...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.msi' -OutFile 'Redis-x64-5.0.14.1.msi' -UseBasicParsing"

echo.
echo 2. 安装 Redis...
msiexec /i "Redis-x64-5.0.14.1.msi" /quiet /norestart

echo.
echo 3. 启动 Redis 服务...
redis-server --service-install
redis-server --service-start

echo.
echo ====================================
echo   Redis 安装完成！
echo ====================================
echo.
echo   服务状态:
sc query Redis
echo.
echo   测试连接:
redis-cli ping
echo.
echo   按任意键退出...
pause >nul