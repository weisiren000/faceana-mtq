@echo off
chcp 65001 >nul
title EmoScan Flutter应用启动器

echo ========================================
echo 🎯 EmoScan 情绪分析系统
echo ========================================
echo.

echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 🚀 启动EmoScan应用...
python run_flutter_app.py

echo.
echo 👋 感谢使用EmoScan！
pause
