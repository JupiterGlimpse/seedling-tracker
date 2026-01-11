#!/bin/bash

echo "================================================"
echo "  AI PM 求职自动化系统 - 环境设置"
echo "================================================"
echo ""

# 检查Python
echo "检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION"
else
    echo "✗ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js（可选）
echo ""
echo "检查Node.js环境（MCP Server需要）..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js $NODE_VERSION"
else
    echo "⚠ 未找到Node.js，MCP Server功能将不可用"
    echo "  安装方法: https://nodejs.org/"
fi

# 安装Python依赖
echo ""
echo "安装Python依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python依赖安装成功"
else
    echo "✗ Python依赖安装失败，请检查网络连接"
    exit 1
fi

# 安装ChromeDriver
echo ""
echo "检查ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✓ ChromeDriver已安装"
else
    echo "⚠ ChromeDriver未安装"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-chromedriver"
    echo "  macOS: brew install chromedriver"
fi

# 安装MCP Server依赖（如果Node.js可用）
if command -v node &> /dev/null; then
    echo ""
    echo "安装MCP Server依赖..."
    cd boss-scraper-mcp
    npm install
    if [ $? -eq 0 ]; then
        echo "✓ MCP Server依赖安装成功"
    else
        echo "✗ MCP Server依赖安装失败"
    fi
    cd ..
fi

# 创建.env文件
echo ""
if [ ! -f .env ]; then
    echo "创建.env配置文件..."
    cp .env.example .env
    echo "✓ 已创建.env文件，请编辑填入实际配置"
else
    echo "✓ .env文件已存在"
fi

# 检查credentials.json
echo ""
if [ ! -f credentials.json ]; then
    echo "⚠ 未找到credentials.json"
    echo "  请按照JOB_AUTOMATION_README.md中的说明配置Google API"
else
    echo "✓ credentials.json已存在"
fi

echo ""
echo "================================================"
echo "  设置完成!"
echo "================================================"
echo ""
echo "下一步:"
echo "1. 配置Google Sheets API（如未完成）"
echo "   - 参考 JOB_AUTOMATION_README.md"
echo ""
echo "2. 设置环境变量（编辑.env文件）"
echo "   - SPREADSHEET_ID"
echo "   - GOOGLE_CREDENTIALS_PATH"
echo ""
echo "3. 运行测试"
echo "   python3 test_job_automation.py"
echo ""
echo "4. (可选) 配置MCP Server"
echo "   - 参考 JOB_AUTOMATION_README.md 的MCP Server配置章节"
echo ""
