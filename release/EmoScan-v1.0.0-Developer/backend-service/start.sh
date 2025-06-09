#!/bin/bash

echo "========================================"
echo "   EmoScan Backend Service Launcher"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python not found! Please install Python 3.8+ first."
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "[INFO] Python found, checking version..."
$PYTHON_CMD --version

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment!"
        exit 1
    fi
fi

# 激活虚拟环境
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# 检查依赖是否安装
echo "[INFO] Checking dependencies..."
if ! pip show fastapi &> /dev/null; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    if [ -f ".env.example" ]; then
        echo "[INFO] Copying .env.example to .env..."
        cp .env.example .env
        echo "[WARNING] Please edit .env file and add your API keys!"
        echo "[WARNING] The application may not work properly without API keys."
        read -p "Press Enter to continue..."
    else
        echo "[ERROR] No .env.example file found!"
        exit 1
    fi
fi

# 启动服务
echo
echo "========================================"
echo "   Starting EmoScan Backend Service"
echo "========================================"
echo "[INFO] Service will start on http://localhost:8000"
echo "[INFO] API documentation: http://localhost:8000/docs"
echo "[INFO] Press Ctrl+C to stop the service"
echo

$PYTHON_CMD start_server.py

# 如果服务异常退出
echo
echo "[INFO] Service stopped."
read -p "Press Enter to exit..."
