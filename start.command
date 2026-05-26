#!/bin/bash
cd "$(dirname "$0")"

echo "========================================"
echo "  智能照片管理系统 - 启动中..."
echo "========================================"
echo ""

# ===== Python 版本检测 =====
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python，请安装 Python 3.10+"
    echo "下载地址: https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

pyver=$(python3 --version 2>&1 | awk '{print $2}')
py_major=$(echo "$pyver" | cut -d. -f1)
py_minor=$(echo "$pyver" | cut -d. -f2)

if [ "$py_major" -lt 3 ] || ([ "$py_major" -eq 3 ] && [ "$py_minor" -lt 10 ]); then
    echo "[错误] 需要 Python 3.10+，当前版本: $pyver"
    echo "下载地址: https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi
echo "[OK] Python $pyver"

# ===== 创建虚拟环境 =====
if [ ! -d "venv" ]; then
    echo "[首次启动] 正在创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 虚拟环境创建失败！"
        echo "可能原因：权限不足或路径含有特殊字符"
        read -p "按回车键退出..."
        exit 1
    fi
fi

source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[错误] 无法激活虚拟环境"
    read -p "按回车键退出..."
    exit 1
fi

# ===== 安装依赖 =====
echo "[检查] 依赖安装状态..."
pip list --format=columns >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[首次启动] 正在安装依赖（可能需要几分钟）..."

    # 离线缓存优先
    if [ -d "requirements_cache" ]; then
        echo "[缓存] 检测到离线依赖缓存，优先从本地安装..."
        pip install --no-index --find-links=requirements_cache -r requirements.txt 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "[缓存] 本地缓存安装失败，尝试从网络安装..."
            pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        fi
    else
        echo "[网络] 从网络安装依赖..."
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    fi

    # 安装失败重试逻辑
    if [ $? -ne 0 ]; then
        echo "[重试 1/3] 安装失败，切换镜像重试..."
        pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    fi
    if [ $? -ne 0 ]; then
        echo "[重试 2/3] 再次尝试默认镜像..."
        pip install -r requirements.txt -i https://pypi.org/simple/
    fi
    if [ $? -ne 0 ]; then
        echo "[重试 3/3] 最后一次尝试..."
        pip install --default-timeout=100 -r requirements.txt
    fi
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败，请检查网络连接后重试"
        read -p "按回车键退出..."
        exit 1
    fi
    echo "[OK] 依赖安装完成"
fi

# ===== 端口检测 =====
PORT=8000
while true; do
    python3 -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1', $PORT)); s.close()" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[OK] 端口 $PORT 可用"
        break
    else
        PORT=$((PORT + 1))
        echo "[提示] 端口 $PORT 被占用，尝试端口 $PORT... "
    fi
done

# 确保 .command 文件可执行
chmod +x "$0"

echo ""
echo "========================================"
echo "  系统准备就绪！"
echo "  访问地址: http://127.0.0.1:$PORT"
echo "  按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 main.py --port $PORT
if [ $? -ne 0 ]; then
    echo "[错误] 系统启动失败，请检查日志"
    read -p "按回车键退出..."
    exit 1
fi
