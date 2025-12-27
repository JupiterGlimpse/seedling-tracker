// INPUT: Express Router，storage 服务，HTTP 请求参数（提醒 ID、操作类型）
// OUTPUT: RESTful API 端点（GET /api/reminders, PUT /api/reminders/:id）
// POS: 路由层，处理提醒相关的 HTTP 请求，支持获取和更新提醒状态
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

const express = require('express');
const router = express.Router();
const storage = require('../services/storage');

// GET /api/reminders - 获取待处理的提醒
router.get('/', async (req, res) => {
  try {
    const reminders = await storage.getPendingReminders();

    res.json({
      success: true,
      data: reminders
    });
  } catch (error) {
    console.error('GET /api/reminders error:', error);
    res.status(500).json({ error: 'Failed to fetch reminders' });
  }
});

// PUT /api/reminders/:id/respond - 响应提醒
router.put('/:id/respond', async (req, res) => {
  try {
    const reminderId = parseInt(req.params.id);
    const { action, pauseDays } = req.body; // action: 'proceed' | 'pause' | 'dismiss'

    if (!action) {
      return res.status(400).json({ error: 'Action is required' });
    }

    // 更新提醒状态为已发送
    await storage.updateReminderStatus(reminderId, 'sent');

    // 根据用户选择更新项目状态
    if (action === 'pause' && pauseDays) {
      // 获取提醒信息以找到对应的项目
      const reminders = await storage.getPendingReminders();
      const reminder = reminders.find(r => r.id === reminderId);

      if (reminder) {
        await storage.updateProjectStatus(
          reminder.project_id,
          'paused',
          pauseDays
        );
      }
    } else if (action === 'dismiss') {
      await storage.updateReminderStatus(reminderId, 'dismissed');
    }
    // 'proceed' 不需要额外操作，项目保持 active 状态

    res.json({
      success: true,
      message: `Reminder ${action}ed successfully`
    });
  } catch (error) {
    console.error('PUT /api/reminders/:id/respond error:', error);
    res.status(500).json({ error: 'Failed to respond to reminder' });
  }
});

module.exports = router;
