// INPUT: Express Router，storage 和 ai 服务，HTTP 请求体（用户输入）
// OUTPUT: RESTful API 端点（POST /api/progress, GET /api/progress）
// POS: 路由层，处理进展记录相关的 HTTP 请求，返回 JSON 响应
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

const express = require('express');
const router = express.Router();
const storage = require('../services/storage');
const ai = require('../services/ai');

// POST /api/progress - 创建新的进展记录
router.post('/', async (req, res) => {
  try {
    const { content } = req.body;

    if (!content || content.trim().length === 0) {
      return res.status(400).json({ error: 'Content is required' });
    }

    // AI 分析内容
    const analysis = await ai.analyzeProgress(content);

    // 查找或创建项目
    const project = await storage.findOrCreateProject(analysis.projectName);

    // 添加进展记录
    const progress = await storage.addProgress(
      project.id,
      content,
      analysis.summary,
      analysis.tags
    );

    // 生成确认消息
    const confirmation = ai.getConfirmationMessage(
      project.name,
      analysis.summary
    );

    res.json({
      success: true,
      message: confirmation,
      data: {
        progress,
        project,
        analysis
      }
    });
  } catch (error) {
    console.error('POST /api/progress error:', error);
    res.status(500).json({ error: 'Failed to create progress entry' });
  }
});

// GET /api/progress - 获取所有进展记录
router.get('/', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50;
    const progressList = await storage.getAllProgress(limit);

    res.json({
      success: true,
      data: progressList
    });
  } catch (error) {
    console.error('GET /api/progress error:', error);
    res.status(500).json({ error: 'Failed to fetch progress' });
  }
});

// GET /api/progress/projects - 获取所有活跃项目
router.get('/projects', async (req, res) => {
  try {
    const projects = await storage.getActiveProjects();

    // 为每个项目获取最新的进展
    const projectsWithProgress = await Promise.all(
      projects.map(async (project) => {
        const recentProgress = await storage.getProgressByProject(project.id, 3);
        return {
          ...project,
          recentProgress
        };
      })
    );

    res.json({
      success: true,
      data: projectsWithProgress
    });
  } catch (error) {
    console.error('GET /api/progress/projects error:', error);
    res.status(500).json({ error: 'Failed to fetch projects' });
  }
});

module.exports = router;
