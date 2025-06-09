@echo off
echo ========================================
echo    EmoScan Backend Service Launcher
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python found, checking version...
python --version

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM 检查依赖是否安装
echo [INFO] Checking dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM 检查环境变量文件
if not exist ".env" (
    echo [WARNING] .env file not found!
    if exist ".env.example" (
        echo [INFO] Copying .env.example to .env...
        copy .env.example .env
        echo [WARNING] Please edit .env file and add your API keys!
        echo [WARNING] The application may not work properly without API keys.
        pause
    ) else (
        echo [ERROR] No .env.example file found!
        pause
        exit /b 1
    )
)

REM 启动服务
echo.
echo ========================================
echo    Starting EmoScan Backend Service
echo ========================================
echo [INFO] Service will start on http://localhost:8000
echo [INFO] API documentation: http://localhost:8000/docs
echo [INFO] Press Ctrl+C to stop the service
echo.

python start_server.py

REM 如果服务异常退出
echo.
echo [INFO] Service stopped.
pause
