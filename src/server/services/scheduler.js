// INPUT: storage 服务（数据库），ai 服务（消息生成），node-cron（定时触发）
// OUTPUT: 自动检查并创建提醒任务
// POS: 定时任务核心，独立运行，定期扫描项目并生成提醒
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

const cron = require('node-cron');
const storage = require('./storage');
const ai = require('./ai');

class SchedulerService {
  constructor() {
    this.task = null;
  }

  // 启动定时任务（每小时检查一次）
  start() {
    // 每小时的第 0 分钟执行
    this.task = cron.schedule('0 * * * *', async () => {
      console.log('🔍 Running reminder check...');
      await this.checkAndCreateReminders();
    });

    console.log('✅ Scheduler started (runs hourly)');

    // 启动后立即执行一次
    this.checkAndCreateReminders();
  }

  // 检查并创建提醒
  async checkAndCreateReminders() {
    try {
      const projects = await storage.getProjectsNeedingReminder();

      if (projects.length === 0) {
        console.log('  No projects need reminder');
        return;
      }

      console.log(`  Found ${projects.length} projects needing reminder`);

      for (const project of projects) {
        // 获取最近的进展记录
        const recentProgress = await storage.getProgressByProject(project.id, 3);

        // 生成提醒消息
        const message = await ai.generateReminderMessage(
          project.name,
          recentProgress
        );

        // 创建提醒记录
        await storage.createReminder(
          project.id,
          message,
          new Date().toISOString()
        );

        console.log(`  ✓ Created reminder for: ${project.name}`);
      }
    } catch (error) {
      console.error('Scheduler error:', error);
    }
  }

  // 停止定时任务
  stop() {
    if (this.task) {
      this.task.stop();
      console.log('⏹️  Scheduler stopped');
    }
  }
}

module.exports = new SchedulerService();
