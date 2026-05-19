@echo off
chcp 65001 >nul
echo =========================================
echo   OKX量化交易系统 - Docker Compose V2 启动
echo =========================================
echo.

REM 检查.env文件是否存在
if not exist .env (
    echo [错误] .env 文件不存在
    echo.
    echo 请先执行以下命令创建配置文件：
    echo   copy .env.example .env
    echo.
    echo 然后编辑 .env 文件，填写您的OKX API密钥
    echo.
    pause
    exit /b 1
)

REM 检查Docker是否安装
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装
    echo.
    echo 请先安装 Docker Desktop:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

REM 检查Docker Compose V2是否安装
docker compose version >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker Compose V2 未安装
    echo.
    echo 请确保 Docker Desktop 版本较新（已内置Compose V2）
    echo 或访问: https://docs.docker.com/compose/install/
    echo.
    pause
    exit /b 1
)

REM 检查Docker是否运行
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker 服务未运行
    echo.
    echo 请启动 Docker Desktop
    echo.
    pause
    exit /b 1
)

echo [检查通过] Docker版本: 
docker --version
echo [检查通过] Docker Compose版本:
docker compose version
echo.

echo [准备] 开始启动系统...
echo.

REM 创建数据目录
if not exist data mkdir data
echo [准备] 数据目录已就绪

REM 检查是否有旧容器在运行
docker compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo [提示] 检测到运行中的容器，先停止...
    docker compose down
    echo.
)

REM 构建并启动服务
echo [构建] 正在构建Docker镜像...
docker compose build

if %errorlevel% neq 0 (
    echo.
    echo [错误] 镜像构建失败
    echo 请查看上方错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo [启动] 正在启动Docker容器...
docker compose up -d

if %errorlevel% neq 0 (
    echo.
    echo [错误] 容器启动失败
    echo 请查看上方错误信息
    echo.
    pause
    exit /b 1
)

REM 等待服务启动
echo.
echo [等待] 等待服务启动（15秒）...
timeout /t 15 /nobreak >nul

REM 检查服务状态
echo.
echo [检查] 验证服务状态...
docker compose ps

echo.
docker compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo.
    echo =========================================
    echo   [成功] 系统启动成功！
    echo =========================================
    echo.
    echo Web界面: http://localhost:5000
    echo.
    echo 常用命令：
    echo   查看日志: docker compose logs -f
    echo   停止服务: docker compose down
    echo   重启服务: docker compose restart
    echo   查看状态: docker compose ps
    echo.
    echo 提示：首次启动需要一些时间初始化数据库
    echo.
    
    REM 询问是否查看日志
    set /p view_logs="是否立即查看日志？(y/n): "
    if /i "%view_logs%"=="y" (
        docker compose logs -f
    )
) else (
    echo.
    echo =========================================
    echo   [错误] 启动失败，请查看日志
    echo =========================================
    echo.
    docker compose logs --tail=50
    echo.
    echo 常见问题：
    echo 1. 检查 .env 文件配置是否正确
    echo 2. 确认端口 5000 未被占用
    echo 3. 查看完整日志: docker compose logs
    echo.
)

pause
