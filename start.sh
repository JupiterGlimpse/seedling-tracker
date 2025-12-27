#!/bin/bash
# 快速启动和测试脚本

echo "🌱 Seedling Tracker - 快速启动"
echo "================================"
echo ""

# 检查 node_modules
if [ ! -d "node_modules" ]; then
  echo "📦 安装依赖..."
  npm install
  if [ $? -ne 0 ]; then
    echo "⚠️  依赖安装失败，使用 Mock 模式继续..."
  fi
fi

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
  echo "📝 创建环境配置文件..."
  cat > .env << 'EOF'
# AI Provider Configuration
AI_PROVIDER=mock

# Anthropic API Key (可选 - 留空使用 Mock 模式)
ANTHROPIC_API_KEY=

# Server Configuration
PORT=3000
EOF
  echo "✅ 已创建 .env 文件（Mock 模式）"
fi

# 初始化数据库
echo "🗄️  初始化数据库..."
node -e "
const storage = require('./src/server/services/storage');
storage.init()
  .then(() => {
    console.log('✅ 数据库初始化完成');
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ 数据库初始化失败:', err.message);
    process.exit(1);
  });
" 2>/dev/null || echo "⚠️  数据库初始化跳过（依赖未安装）"

echo ""
echo "🚀 启动服务器..."
echo "================================"
echo ""

# 启动服务
node src/server/index.js
