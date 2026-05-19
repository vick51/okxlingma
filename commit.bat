@echo off
chcp 65001 >nul
echo =========================================
echo   Git 自动提交脚本
echo =========================================
echo.

REM 检查是否在Git仓库中
if not exist .git (
    echo [错误] 当前目录不是Git仓库
    pause
    exit /b 1
)

REM 显示当前状态
echo [状态] 当前Git状态:
git status --short
echo.

REM 添加所有更改
echo [添加] 添加所有更改...
git add .

if %errorlevel% neq 0 (
    echo [错误] 添加文件失败
    pause
    exit /b 1
)

REM 获取当前时间作为提交信息
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set commit_msg="自动提交: %datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%"

REM 如果有更新则提交
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [提示] 没有需要提交的更改
    pause
    exit /b 0
)

echo [提交] 提交更改...
echo 提交信息: %commit_msg%
git commit -m %commit_msg%

if %errorlevel% equ 0 (
    echo.
    echo =========================================
    echo   [成功] 提交完成
    echo =========================================
    echo.
    
    REM 询问是否推送
    set /p push_now="是否推送到远程仓库？(y/n): "
    if /i "%push_now%"=="y" (
        echo [推送] 正在推送...
        git push
        
        if %errorlevel% equ 0 (
            echo [成功] 推送完成
        ) else (
            echo [错误] 推送失败
        )
    )
) else (
    echo [错误] 提交失败
)

echo.
pause
