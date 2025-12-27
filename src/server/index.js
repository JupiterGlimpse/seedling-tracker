// INPUT: 环境变量配置，Express 框架，routes 和 services 模块
// OUTPUT: 启动的 HTTP 服务器（监听端口 3000）
// POS: 服务器入口，初始化所有服务并启动 Express 应用
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

require('dotenv').config();
const express = require('express');
const path = require('path');
const storage = require('./services/storage');
const ai = require('./services/ai');
const scheduler = require('./services/scheduler');
const progressRoutes = require('./routes/progress');
const reminderRoutes = require('./routes/reminder');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务（前端）
app.use(express.static(path.join(__dirname, '../client')));

// API 路由
app.use('/api/progress', progressRoutes);
app.use('/api/reminders', reminderRoutes);

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 初始化并启动服务器
async function start() {
  try {
    console.log('🚀 Starting Seedling Tracker...\n');

    // 初始化数据库
    await storage.init();

    // 初始化 AI 服务
    ai.init();

    // 启动定时任务
    scheduler.start();

    // 启动 HTTP 服务器
    app.listen(PORT, () => {
      console.log(`\n✨ Server running at http://localhost:${PORT}`);
      console.log('📝 Open browser to start tracking progress!\n');
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down gracefully...');
  scheduler.stop();
  process.exit(0);
});

start();
