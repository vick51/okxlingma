@echo off
chcp 65001 >nul
echo =========================================
echo   OKX量化交易系统 - Docker Compose 停止
echo =========================================
echo.

REM 检查Docker是否运行
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker 服务未运行
    pause
    exit /b 1
)

REM 检查容器是否运行
docker-compose ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [提示] 没有运行中的容器
    pause
    exit /b 0
)

echo [提示] 即将停止OKX量化交易系统
echo.
set /p confirm="确认停止？(y/n): "
if /i not "%confirm%"=="y" (
    echo [取消] 操作已取消
    pause
    exit /b 0
)

echo.
echo [停止] 正在停止容器...
docker-compose down

if %errorlevel% equ 0 (
    echo.
    echo =========================================
    echo   [成功] 系统已停止
    echo =========================================
    echo.
    echo 数据已保存至 data/ 目录
    echo 下次启动时会自动恢复
    echo.
) else (
    echo.
    echo [错误] 停止失败
    docker-compose logs --tail=20
)

pause
