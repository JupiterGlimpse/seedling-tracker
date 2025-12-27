#!/bin/bash
#=====================================
# Seedling Tracker - 一键启动脚本
# 遵循 Linus 哲学：简单、直接、无废话
#=====================================

set -e  # 任何错误立即退出

echo "🌱 Seedling Tracker"
echo ""

# ────────────────────────────────────
# 依赖检查（首次运行时安装）
# ────────────────────────────────────
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install --silent || {
        echo "⚠️  npm install 失败，使用 Mock 模式继续"
    }
fi

# ────────────────────────────────────
# 环境配置（自动创建最小配置）
# ────────────────────────────────────
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Mock 模式（无需 API Key）
AI_PROVIDER=mock
PORT=3000

# 可选：配置 Anthropic API Key 启用完整 AI 功能
# ANTHROPIC_API_KEY=your_key_here
EOF
    echo "✅ 创建 .env（Mock 模式）"
fi

# ────────────────────────────────────
# 启动服务（数据库自动初始化）
# ────────────────────────────────────
echo "🚀 启动服务..."
echo ""

node src/server/index.js
