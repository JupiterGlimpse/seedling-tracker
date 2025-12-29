#!/bin/bash

echo "======================================"
echo "  Memory Agent 前端启动脚本"
echo "======================================"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并配置你的 OPENAI_API_KEY"
    echo ""
    echo "命令: cp .env.example .env"
    echo "然后编辑 .env 文件添加你的 API Key"
    echo ""
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip list | grep -q flask || {
    echo "⚠️  未安装依赖，正在安装..."
    pip install -r requirements.txt
}

echo ""
echo "✅ 准备就绪！"
echo ""
echo "🚀 启动服务器..."
echo "📱 访问地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python app.py
