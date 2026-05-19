@echo off
chcp 65001 >nul
echo =========================================
echo   OKX量化交易系统 - Docker Compose V2 重启
echo =========================================
echo.

REM 检查Docker是否运行
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker 服务未运行
    pause
    exit /b 1
)

echo [重启] 正在重启服务...
docker compose restart

if %errorlevel% equ 0 (
    echo.
    echo [等待] 等待服务启动（10秒）...
    timeout /t 10 /nobreak >nul
    
    echo.
    echo [检查] 服务状态...
    docker compose ps
    
    echo.
    echo =========================================
    echo   [成功] 服务已重启
    echo =========================================
    echo.
    echo Web界面: http://localhost:5000
    echo.
) else (
    echo.
    echo [错误] 重启失败
    echo 尝试完全重启...
    docker compose down
    docker compose up -d
)

pause
