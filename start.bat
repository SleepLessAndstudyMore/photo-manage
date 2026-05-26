@echo off
chcp 65001 >nul
echo ========================================
echo   智能照片管理系统 - 启动中...
echo ========================================

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "venv" (
    echo [首次启动] 正在创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [首次启动] 正在安装依赖（可能需要几分钟）...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    call venv\Scripts\activate.bat
)

python main.py
