#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚗 車用儀表板 - CAN模擬器啟動腳本${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 檢查Python版本
echo -e "${YELLOW}📋 檢查Python版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到Python3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}\n"

# 檢查和安裝依賴
echo -e "${YELLOW}📦 檢查並安裝依賴...${NC}"
pip_packages="cantools"

for package in $pip_packages; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package 已安裝${NC}"
    else
        echo -e "${YELLOW}⬇️  正在安裝 $package...${NC}"
        pip install $package
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ $package 安裝成功${NC}"
        else
            echo -e "${RED}❌ $package 安裝失敗${NC}"
            exit 1
        fi
    fi
done

echo ""
echo -e "${GREEN}✅ 所有依賴已就緒！${NC}\n"

# 顯示文件結構
echo -e "${YELLOW}📁 專案檔案:${NC}"
ls -lh *.py *.dbc *.md 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
echo ""

# 給出啟動选項
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🚀 快速开始 - 選擇模式:${NC}\n"
echo "1) 啟動模擬器 (主程序)"
echo "2) 啟動客戶端 (資料查看) - 需在另一個終端執行"
echo "3) 在两个終端中同时啟動 (自動化)"
echo "4) 查看README文件"
echo "5) 離開"
echo ""

read -p "請選擇 [1-5]: " choice

case $choice in
    1)
        echo -e "\n${BLUE}啟動模擬器...${NC}\n"
        python3 can_simulator.py
        ;;
    2)
        echo -e "\n${BLUE}啟動客戶端...${NC}\n"
        python3 can_client.py
        ;;
    3)
        echo -e "\n${BLUE}在两个終端中啟動模擬器和客戶端...${NC}\n"
        echo -e "${YELLOW}💡 提示: 你可以在两个終端窗口中分别執行:${NC}"
        echo -e "   ${GREEN}終端1: python3 can_simulator.py${NC}"
        echo -e "   ${GREEN}終端2: python3 can_client.py${NC}\n"
        
        # 嘗試在新終端打开 (支持Linux)
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "python3 can_simulator.py; bash"
            sleep 2
            gnome-terminal -- bash -c "python3 can_client.py; bash"
            echo -e "${GREEN}✅ 已在新終端中啟動${NC}\n"
        elif command -v xterm &> /dev/null; then
            xterm -e "python3 can_simulator.py" &
            sleep 2
            xterm -e "python3 can_client.py" &
            echo -e "${GREEN}✅ 已在新終端中啟動${NC}\n"
        else
            echo -e "${YELLOW}⚠️  未偵測到終端模擬器，請手动在两个終端中執行:${NC}"
            echo -e "   ${GREEN}終端1: python3 can_simulator.py${NC}"
            echo -e "   ${GREEN}終端2: python3 can_client.py${NC}\n"
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
        echo -e "${RED}❌ 無效的選擇${NC}"
        exit 1
        ;;
esac
