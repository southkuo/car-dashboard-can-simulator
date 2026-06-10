#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     🚗 车用仪表板 CAN模拟器 - GitHub 初始化脚本              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# 检查git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装，请先安装Git${NC}"
    exit 1
fi

# 检查是否已是git仓库
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  当前目录已是git仓库${NC}"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo -e "${BLUE}📋 初始化Git仓库...${NC}\n"
    git init
    echo -e "${GREEN}✅ Git仓库初始化完成\n${NC}"
fi

# 配置git用户信息
echo -e "${BLUE}⚙️  配置Git用户信息${NC}\n"

read -p "输入你的GitHub用户名 (例: username): " github_username
read -p "输入你的GitHub邮箱 (例: email@example.com): " github_email

if [ -z "$github_username" ] || [ -z "$github_email" ]; then
    echo -e "${RED}❌ 用户名或邮箱不能为空${NC}"
    exit 1
fi

# 设置git用户信息
git config --global user.name "$github_username"
git config --global user.email "$github_email"

echo -e "${GREEN}✅ 用户信息配置完成${NC}\n"

# 添加所有文件
echo -e "${BLUE}📁 添加文件到Git...${NC}\n"
git add .
echo -e "${GREEN}✅ 所有文件已添加\n${NC}"

# 创建初始提交
echo -e "${BLUE}💾 创建初始提交...${NC}\n"
git commit -m "🎉 Initial commit: Python CAN simulator for car dashboard

Features:
- Complete CAN simulator with DBC parsing
- Realistic signal simulation (RPM, speed, temperature, fuel level)
- TCP/JSON communication protocol
- Test client and analysis tools
- Comprehensive documentation

Ready for Qt6 integration."

echo -e "${GREEN}✅ 初始提交完成\n${NC}"

# 显示GitHub设置说明
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}📌 下一步：创建GitHub仓库并推送${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}1️⃣  在GitHub上创建新仓库:${NC}"
echo -e "   • 访问 ${YELLOW}https://github.com/new${NC}"
echo -e "   • 仓库名称: ${YELLOW}car-dashboard-can-simulator${NC}"
echo -e "   • 描述: ${YELLOW}Python CAN Simulator for Car Dashboard with Qt6${NC}"
echo -e "   • 可见性: 选择 ${YELLOW}Public${NC} (公开) 或 ${YELLOW}Private${NC} (私密)"
echo -e "   • ${RED}⚠️ 不要${NC}勾选 Initialize with README${NC}\n"

echo -e "${BLUE}2️⃣  复制仓库URL，形式如下:${NC}"
echo -e "   ${YELLOW}https://github.com/YOUR_USERNAME/car-dashboard-can-simulator.git${NC}"
echo -e "   或使用SSH:"
echo -e "   ${YELLOW}git@github.com:YOUR_USERNAME/car-dashboard-can-simulator.git${NC}\n"

echo -e "${BLUE}3️⃣  在下方输入你的仓库URL:${NC}\n"

read -p "请输入GitHub仓库URL: " repo_url

if [ -z "$repo_url" ]; then
    echo -e "${YELLOW}⚠️  跳过远程仓库设置${NC}"
    echo -e "\n你可以稍后手动运行:"
    echo -e "${YELLOW}git remote add origin <你的仓库URL>${NC}"
    echo -e "${YELLOW}git branch -M main${NC}"
    echo -e "${YELLOW}git push -u origin main${NC}\n"
    exit 0
fi

# 添加远程仓库
echo -e "\n${BLUE}🔗 添加远程仓库...${NC}"
git remote add origin "$repo_url"
echo -e "${GREEN}✅ 远程仓库已添加\n${NC}"

# 重命名分支为main
echo -e "${BLUE}🌳 重命名默认分支为 main...${NC}"
git branch -M main
echo -e "${GREEN}✅ 分支已重命名\n${NC}"

# 推送到GitHub
echo -e "${BLUE}📤 推送到GitHub...${NC}\n"
echo -e "${YELLOW}提示: 这将要求你输入GitHub凭证（token或密码）${NC}\n"

git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ 成功推送到GitHub!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"
    
    echo -e "${BLUE}📊 推送统计:${NC}"
    echo -e "   用户名: ${YELLOW}$github_username${NC}"
    echo -e "   仓库URL: ${YELLOW}$repo_url${NC}"
    echo -e "   分支: ${YELLOW}main${NC}\n"
    
    echo -e "${BLUE}🔗 访问你的仓库:${NC}"
    echo -e "   ${YELLOW}$(echo $repo_url | sed 's/.git$//')${NC}\n"
    
    echo -e "${BLUE}💡 后续操作:${NC}"
    echo -e "   1. 本地修改后: ${YELLOW}git add .${NC}"
    echo -e "   2. 提交: ${YELLOW}git commit -m '你的提交信息'${NC}"
    echo -e "   3. 推送: ${YELLOW}git push${NC}\n"
    
else
    echo -e "\n${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ 推送失败，请检查:${NC}"
    echo -e "   1. 网络连接${NC}"
    echo -e "   2. 仓库URL是否正确${NC}"
    echo -e "   3. GitHub凭证是否有效${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}\n"
    
    echo -e "${YELLOW}手动推送命令:${NC}"
    echo -e "   ${YELLOW}git remote set-url origin ${repo_url}${NC}"
    echo -e "   ${YELLOW}git push -u origin main${NC}\n"
fi

echo -e "${BLUE}📚 更多信息:${NC}"
echo -e "   • 查看git状态: ${YELLOW}git status${NC}"
echo -e "   • 查看提交历史: ${YELLOW}git log${NC}"
echo -e "   • 查看远程仓库: ${YELLOW}git remote -v${NC}\n"

echo -e "${GREEN}🎉 GitHub初始化脚本完成!${NC}\n"
