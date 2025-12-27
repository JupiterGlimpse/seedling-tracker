# Seedling Tracker 快速诊断脚本

echo "🔍 Seedling Tracker 系统诊断"
echo "================================"
echo ""

# 1. 检查环境变量
echo "1️⃣ 环境变量检查："
if [ -f ".env" ]; then
    echo "   ✅ .env 文件存在"
    if grep -q "ANTHROPIC_API_KEY=.\+" .env 2>/dev/null; then
        echo "   ✅ API Key 已配置"
    else
        echo "   ⚠️  API Key 未配置 → 将使用 Mock 模式"
    fi
else
    echo "   ⚠️  .env 文件不存在 → 将使用 Mock 模式"
fi
echo ""

# 2. 检查服务器状态
echo "2️⃣ 服务器状态："
if ps aux | grep -v grep | grep "node.*server/index.js" > /dev/null; then
    echo "   ✅ 服务器正在运行"
else
    echo "   ❌ 服务器未运行"
    echo "   → 需要执行：npm start"
fi
echo ""

# 3. 检查端口
echo "3️⃣ 端口检查："
if lsof -i :3000 > /dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q :3000; then
    echo "   ✅ 端口 3000 已占用（服务运行中或冲突）"
else
    echo "   ⚠️  端口 3000 空闲（服务未启动）"
fi
echo ""

# 4. 检查依赖
echo "4️⃣ 依赖检查："
if [ -d "node_modules" ]; then
    echo "   ✅ node_modules 存在"
else
    echo "   ❌ 依赖未安装"
    echo "   → 需要执行：npm install"
fi
echo ""

# 5. 检查数据库
echo "5️⃣ 数据库检查："
if [ -f "src/server/db/database.db" ]; then
    echo "   ✅ 数据库文件存在"
else
    echo "   ⚠️  数据库未初始化"
    echo "   → 将在首次启动时自动创建"
fi
echo ""

echo "================================"
echo "💡 诊断完成！"
echo ""
echo "📝 建议操作："
echo "   1. 如果服务器未运行：npm start"
echo "   2. 如果依赖未安装：npm install && npm start"
echo "   3. 如果需要 AI 功能：配置 .env 中的 ANTHROPIC_API_KEY"
echo ""
