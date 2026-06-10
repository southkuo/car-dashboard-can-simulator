@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 颜色定义
REM Windows命令行有限制，使用简单输出

echo.
echo ========================================================
echo     车用仪表板 CAN模拟器 - Windows 推送脚本
echo     仓库: southkuo/car-dashboard-can-simulator
echo ========================================================
echo.

REM 检查Git是否安装
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Git未安装，请先安装Git
    echo 下载: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [✓] Git已安装
echo.

REM 远程仓库URL
set REPO_URL=https://github.com/southkuo/car-dashboard-can-simulator.git

echo [信息] 仓库: %REPO_URL%
echo.

REM 检查是否已是git仓库
if not exist ".git" (
    echo [步骤1] 初始化Git仓库...
    call git init
    if %errorlevel% neq 0 (
        echo [错误] Git初始化失败
        pause
        exit /b 1
    )
    echo [✓] Git初始化完成
    echo.
    
    REM 配置用户（如果需要）
    for /f "tokens=*" %%a in ('git config user.name') do set GIT_USER=%%a
    if "!GIT_USER!"=="" (
        echo [步骤2] 配置Git用户信息...
        set /p GIT_USER=输入GitHub用户名 [southkuo]: 
        if "!GIT_USER!"=="" set GIT_USER=southkuo
        
        set /p GIT_EMAIL=输入GitHub邮箱: 
        if "!GIT_EMAIL!"=="" (
            echo [错误] 邮箱不能为空
            pause
            exit /b 1
        )
        
        call git config --local user.name "!GIT_USER!"
        call git config --local user.email "!GIT_EMAIL!"
        echo [✓] 用户信息已配置
        echo.
    )
) else (
    echo [信息] 目录已是git仓库
    echo.
)

REM 添加所有文件
echo [步骤3] 添加文件到Git...
call git add .
if %errorlevel% neq 0 (
    echo [错误] 添加文件失败
    pause
    exit /b 1
)
echo [✓] 文件已添加
echo.

REM 检查是否有未提交的更改
git diff-index --quiet HEAD -- 2>nul
if %errorlevel% neq 0 (
    REM 有更改，创建提交
    echo [步骤4] 创建提交...
    call git commit -m "Initial commit: Python CAN simulator for car dashboard"
    if %errorlevel% neq 0 (
        echo [警告] 提交失败或没有更改
    ) else (
        echo [✓] 提交已创建
    )
    echo.
) else (
    echo [信息] 没有新的更改
    echo.
)

REM 检查远程仓库
echo [步骤5] 检查远程仓库...
call git remote | find "origin" >nul
if %errorlevel% equ 0 (
    echo [信息] 远程仓库已存在
    for /f "tokens=*" %%a in ('git remote get-url origin') do set CURRENT_URL=%%a
    echo 当前: !CURRENT_URL!
    echo 目标: %REPO_URL%
    echo.
    set /p UPDATE_REMOTE=是否更新远程仓库地址? (y/n) [n]: 
    if /i "!UPDATE_REMOTE!"=="y" (
        call git remote set-url origin "%REPO_URL%"
        echo [✓] 远程仓库已更新
        echo.
    )
) else (
    echo [添加] 添加远程仓库...
    call git remote add origin "%REPO_URL%"
    if %errorlevel% neq 0 (
        echo [错误] 添加远程仓库失败
        pause
        exit /b 1
    )
    echo [✓] 远程仓库已添加
    echo.
)

REM 检查分支
echo [步骤6] 检查分支...
for /f "tokens=*" %%a in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%a
echo 当前分支: !CURRENT_BRANCH!

if not "!CURRENT_BRANCH!"=="main" (
    echo [重命名] 重命名为main...
    call git branch -M main
    echo [✓] 分支已重命名为main
    echo.
) else (
    echo [✓] 已在main分支
    echo.
)

REM 推送到GitHub
echo [步骤7] 推送到GitHub...
echo [提示] 这将要求你输入GitHub凭证
echo.

call git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo [✓] 成功推送到GitHub!
    echo ========================================================
    echo.
    echo [信息] 推送完成:
    echo   仓库: %REPO_URL%
    echo   分支: main
    echo.
    echo [链接] 访问你的仓库:
    echo   https://github.com/southkuo/car-dashboard-can-simulator
    echo.
    echo [后续] 下一步操作:
    echo   1. git add . ^&^& git commit -m "说明"
    echo   2. git push
    echo.
) else (
    echo.
    echo ========================================================
    echo [错误] 推送失败
    echo ========================================================
    echo.
    echo [排查] 检查以下项:
    echo   1. 网络连接是否正常
    echo   2. 仓库URL是否正确
    echo   3. GitHub凭证是否有效
    echo   4. 仓库是否已在GitHub创建
    echo.
    echo [手动] 尝试手动推送:
    echo   git push -u origin main
    echo.
)

pause
