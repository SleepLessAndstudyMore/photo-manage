@echo off
chcp 65001 >nul
title 智能照片管理系统
setlocal enabledelayedexpansion

echo ========================================
echo   智能照片管理系统 - 启动中...
echo ========================================
echo.

REM ===== Python 版本检测 =====
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set pyver=%%i

REM 解析主版本和次版本（支持 3.10、3.11、3.12 等两位数次版本）
for /f "tokens=1,2 delims=." %%a in ("%pyver%") do (
    set py_major=%%a
    set py_minor=%%b
)

if %py_major% lss 3 (
    echo [错误] 需要 Python 3.10+，当前版本: %pyver%
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
if %py_minor% lss 10 (
    echo [错误] 需要 Python 3.10+，当前版本: %pyver%
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python %pyver%

REM ===== 创建虚拟环境 =====
if not exist "venv" (
    echo [首次启动] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败！
        echo 可能原因：权限不足或路径含有特殊字符
        echo 请尝试以管理员身份运行，或将项目移动到无中文/空格的路径
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 无法激活虚拟环境
    pause
    exit /b 1
)

REM ===== 检查依赖是否已安装 =====
echo [检查] 依赖安装状态...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [首次启动] 正在安装依赖（可能需要几分钟）...

    REM 离线缓存优先
    if exist "requirements_cache" (
        echo [缓存] 检测到离线依赖缓存，优先从本地安装...
        pip install --no-index --find-links=requirements_cache -r requirements.txt
        if errorlevel 1 (
            echo [缓存] 本地缓存安装失败，尝试从网络安装...
            pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        )
    ) else (
        echo [网络] 从网络安装依赖...
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    )

    REM 安装失败重试逻辑
    if errorlevel 1 (
        echo [重试 1/3] 安装失败，切换镜像重试...
        pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    )
    if errorlevel 1 (
        echo [重试 2/3] 再次尝试默认镜像...
        pip install -r requirements.txt -i https://pypi.org/simple/
    )
    if errorlevel 1 (
        echo [重试 3/3] 最后一次尝试...
        pip install --default-timeout=100 -r requirements.txt
    )
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络连接后重试
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
) else (
    echo [OK] 依赖已就绪
)

REM ===== 端口检测 =====
set PORT=8000
:check_port
python -c "import socket; s=socket.socket(); s.settimeout(0.5); s.connect(('127.0.0.1', %PORT%)); s.close()" >nul 2>&1
if errorlevel 1 (
    echo [OK] 端口 %PORT% 可用
) else (
    set /a PORT+=1
    echo [提示] 端口 %PORT% 被占用，尝试端口 !PORT!...
    goto check_port
)

REM ===== 启动 =====
echo.
echo ========================================
echo   系统准备就绪！
echo   访问地址: http://127.0.0.1:%PORT%
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

python main.py --port %PORT%
if errorlevel 1 (
    echo [错误] 系统启动失败，请检查日志
    pause
    exit /b 1
)

pause
