# Windows PowerShell 推送脚本 - 车用仪表板CAN模拟器
# 使用方法: powershell -ExecutionPolicy Bypass -File push_to_southkuo.ps1

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚗 车用仪表板 CAN模拟器 - Windows 推送脚本                ║" -ForegroundColor Cyan
Write-Host "║     仓库: southkuo/car-dashboard-can-simulator               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查Git
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "[❌] Git未安装，请先安装Git" -ForegroundColor Red
    Write-Host "下载: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "或使用Chocolatey: choco install git" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host "[✅] Git已安装" -ForegroundColor Green
Write-Host ""

# 仓库URL
$repoUrl = "https://github.com/southkuo/car-dashboard-can-simulator.git"

Write-Host "[信息] 仓库: $repoUrl" -ForegroundColor Yellow
Write-Host ""

# 步骤1: 初始化Git
if (-not (Test-Path .git)) {
    Write-Host "[步骤1] 初始化Git仓库..." -ForegroundColor Cyan
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[❌] Git初始化失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "[✅] Git初始化完成" -ForegroundColor Green
    Write-Host ""
    
    # 配置用户
    $gitUser = git config user.name 2>$null
    if (-not $gitUser) {
        Write-Host "[步骤2] 配置Git用户信息..." -ForegroundColor Cyan
        
        $userName = Read-Host "输入GitHub用户名 [southkuo]"
        if ([string]::IsNullOrEmpty($userName)) { $userName = "southkuo" }
        
        $userEmail = Read-Host "输入GitHub邮箱"
        if ([string]::IsNullOrEmpty($userEmail)) {
            Write-Host "[❌] 邮箱不能为空" -ForegroundColor Red
            Read-Host "按Enter键退出"
            exit 1
        }
        
        git config --local user.name $userName
        git config --local user.email $userEmail
        
        Write-Host "[✅] 用户信息已配置" -ForegroundColor Green
        Write-Host ""
    }
} else {
    Write-Host "[信息] 目录已是git仓库" -ForegroundColor Yellow
    Write-Host ""
}

# 步骤2: 添加文件
Write-Host "[步骤3] 添加文件到Git..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[❌] 添加文件失败" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}
Write-Host "[✅] 文件已添加" -ForegroundColor Green
Write-Host ""

# 步骤3: 创建提交
Write-Host "[步骤4] 创建提交..." -ForegroundColor Cyan
$status = git diff-index --quiet HEAD -- 2>$null
if ($LASTEXITCODE -ne 0) {
    git commit -m "Initial commit: Python CAN simulator for car dashboard

Features:
- Complete CAN simulator with DBC parsing
- Realistic signal simulation (RPM, speed, temperature, fuel level)
- TCP/JSON communication protocol
- Test client and analysis tools
- Comprehensive documentation

Ready for Qt6 integration."
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✅] 提交已创建" -ForegroundColor Green
    } else {
        Write-Host "[⚠️] 提交失败或没有更改" -ForegroundColor Yellow
    }
} else {
    Write-Host "[信息] 没有新的更改" -ForegroundColor Yellow
}
Write-Host ""

# 步骤4: 检查远程仓库
Write-Host "[步骤5] 检查远程仓库..." -ForegroundColor Cyan
$remotes = git remote
if ($remotes -contains "origin") {
    Write-Host "[信息] 远程仓库已存在" -ForegroundColor Yellow
    $currentUrl = git remote get-url origin
    Write-Host "  当前: $currentUrl" -ForegroundColor Yellow
    Write-Host "  目标: $repoUrl" -ForegroundColor Yellow
    Write-Host ""
    
    $update = Read-Host "是否更新远程仓库地址? (y/n) [n]"
    if ($update -eq "y" -or $update -eq "Y") {
        git remote set-url origin $repoUrl
        Write-Host "[✅] 远程仓库已更新" -ForegroundColor Green
        Write-Host ""
    }
} else {
    Write-Host "[步骤5] 添加远程仓库..." -ForegroundColor Cyan
    git remote add origin $repoUrl
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[❌] 添加远程仓库失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "[✅] 远程仓库已添加" -ForegroundColor Green
    Write-Host ""
}

# 步骤5: 检查分支
Write-Host "[步骤6] 检查分支..." -ForegroundColor Cyan
$currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
Write-Host "  当前分支: $currentBranch" -ForegroundColor Yellow

if ($currentBranch -ne "main") {
    Write-Host "[重命名] 重命名为main..." -ForegroundColor Cyan
    git branch -M main
    Write-Host "[✅] 分支已重命名为main" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[✅] 已在main分支" -ForegroundColor Green
    Write-Host ""
}

# 步骤6: 推送
Write-Host "[步骤7] 推送到GitHub..." -ForegroundColor Cyan
Write-Host "[提示] 这将要求你输入GitHub凭证" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║ [✅] 成功推送到GitHub!                                         ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "[信息] 推送完成:" -ForegroundColor Cyan
    Write-Host "  仓库: $repoUrl" -ForegroundColor Green
    Write-Host "  分支: main" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "[链接] 访问你的仓库:" -ForegroundColor Cyan
    Write-Host "  https://github.com/southkuo/car-dashboard-can-simulator" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "[后续] 下一步操作:" -ForegroundColor Cyan
    Write-Host "  1. git add . && git commit -m '说明'" -ForegroundColor Yellow
    Write-Host "  2. git push" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║ [❌] 推送失败                                                  ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "[排查] 检查以下项:" -ForegroundColor Yellow
    Write-Host "  1. 网络连接是否正常" -ForegroundColor Yellow
    Write-Host "  2. 仓库URL是否正确" -ForegroundColor Yellow
    Write-Host "  3. GitHub凭证是否有效" -ForegroundColor Yellow
    Write-Host "  4. 仓库是否已在GitHub创建" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "[手动] 尝试手动推送:" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "按Enter键退出"
