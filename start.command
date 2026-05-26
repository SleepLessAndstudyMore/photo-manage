#!/bin/bash
cd "$(dirname "$0")"

echo "========================================"
echo "  智能照片管理系统 - 启动中..."
echo "========================================"

if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python，请安装 Python 3.10+"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[首次启动] 正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[首次启动] 正在安装依赖（可能需要几分钟）..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
else
    source venv/bin/activate
fi

python3 main.py
