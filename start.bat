@echo off
cd /d "%~dp0"

echo ========================================
echo   Starting Photo Manager...
echo ========================================

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo Starting server at http://127.0.0.1:8000
python main.py
pause
