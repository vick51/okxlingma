@echo off
echo =========================================
echo   OKX量化交易系统 - 启动脚本
echo =========================================
echo.

REM 检查.env文件是否存在
if not exist .env (
    echo [错误] .env 文件不存在
    echo 请先复制示例配置并填写您的API密钥:
    echo   copy .env.example .env
    echo 然后编辑 .env 文件
    pause
    exit /b 1
)

REM 检查Docker是否安装
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装
    echo 请先安装 Docker: https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)

echo [检查通过] 开始启动...
echo.

REM 创建数据目录
if not exist data mkdir data

REM 启动服务
echo [启动] 正在启动Docker容器...
docker-compose up -d

REM 等待服务启动
echo [等待] 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo.
    echo =========================================
    echo   [成功] 系统启动成功！
    echo =========================================
    echo.
    echo Web界面: http://localhost:5000
    echo 查看日志: docker-compose logs -f
    echo 停止服务: docker-compose down
    echo.
) else (
    echo.
    echo =========================================
    echo   [错误] 启动失败，请查看日志
    echo =========================================
    echo.
    docker-compose logs
)

pause
