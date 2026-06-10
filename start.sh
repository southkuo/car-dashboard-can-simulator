#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚗 车用仪表板 - CAN模拟器启动脚本${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 检查Python版本
echo -e "${YELLOW}📋 检查Python版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到Python3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}\n"

# 检查和安装依赖
echo -e "${YELLOW}📦 检查并安装依赖...${NC}"
pip_packages="cantools"

for package in $pip_packages; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package 已安装${NC}"
    else
        echo -e "${YELLOW}⬇️  正在安装 $package...${NC}"
        pip install $package
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ $package 安装成功${NC}"
        else
            echo -e "${RED}❌ $package 安装失败${NC}"
            exit 1
        fi
    fi
done

echo ""
echo -e "${GREEN}✅ 所有依赖已就绪！${NC}\n"

# 显示文件结构
echo -e "${YELLOW}📁 项目文件:${NC}"
ls -lh *.py *.dbc *.md 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
echo ""

# 给出启动选项
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🚀 快速开始 - 选择模式:${NC}\n"
echo "1) 启动模拟器 (主程序)"
echo "2) 启动客户端 (数据查看) - 需在另一个终端运行"
echo "3) 在两个终端中同时启动 (自动化)"
echo "4) 查看README文档"
echo "5) 退出"
echo ""

read -p "请选择 [1-5]: " choice

case $choice in
    1)
        echo -e "\n${BLUE}启动模拟器...${NC}\n"
        python3 can_simulator.py
        ;;
    2)
        echo -e "\n${BLUE}启动客户端...${NC}\n"
        python3 can_client.py
        ;;
    3)
        echo -e "\n${BLUE}在两个终端中启动模拟器和客户端...${NC}\n"
        echo -e "${YELLOW}💡 提示: 你可以在两个终端窗口中分别运行:${NC}"
        echo -e "   ${GREEN}终端1: python3 can_simulator.py${NC}"
        echo -e "   ${GREEN}终端2: python3 can_client.py${NC}\n"
        
        # 尝试在新终端打开 (支持Linux)
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "python3 can_simulator.py; bash"
            sleep 2
            gnome-terminal -- bash -c "python3 can_client.py; bash"
            echo -e "${GREEN}✅ 已在新终端中启动${NC}\n"
        elif command -v xterm &> /dev/null; then
            xterm -e "python3 can_simulator.py" &
            sleep 2
            xterm -e "python3 can_client.py" &
            echo -e "${GREEN}✅ 已在新终端中启动${NC}\n"
        else
            echo -e "${YELLOW}⚠️  未检测到终端仿真器，请手动在两个终端中运行:${NC}"
            echo -e "   ${GREEN}终端1: python3 can_simulator.py${NC}"
            echo -e "   ${GREEN}终端2: python3 can_client.py${NC}\n"
        fi
        ;;
    4)
        if command -v less &> /dev/null; then
            less README.md
        else
            cat README.md
        fi
        ;;
    5)
        echo -e "\n${GREEN}👋 再见！${NC}\n"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ 无效的选择${NC}"
        exit 1
        ;;
esac
