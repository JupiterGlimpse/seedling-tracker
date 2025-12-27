// INPUT: 用户输入的文本内容，环境变量中的 AI API Key
// OUTPUT: 项目分类、内容摘要、提醒消息生成等 AI 分析结果
// POS: AI 服务核心，封装所有 AI 调用，被 routes 和 scheduler 使用
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

const Anthropic = require('@anthropic-ai/sdk');

class AIService {
  constructor() {
    this.client = null;
    this.apiKey = process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY;
    this.provider = process.env.AI_PROVIDER || 'anthropic'; // anthropic or openai
  }

  init() {
    if (this.provider === 'anthropic' && process.env.ANTHROPIC_API_KEY) {
      this.client = new Anthropic({
        apiKey: process.env.ANTHROPIC_API_KEY
      });
      console.log('✅ AI Service initialized (Anthropic)');
    } else if (this.provider === 'openai' && process.env.OPENAI_API_KEY) {
      // OpenAI 集成预留
      console.log('⚠️  OpenAI provider not yet implemented, using mock mode');
    } else {
      console.log('⚠️  No AI API key found, using mock mode');
    }
  }

  // 分析用户输入，提取项目名称和摘要
  async analyzeProgress(content) {
    if (!this.client) {
      // Mock mode for development
      return {
        projectName: 'Default Project',
        summary: content.substring(0, 50) + '...',
        tags: ['general']
      };
    }

    try {
      const message = await this.client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 300,
        messages: [{
          role: 'user',
          content: `分析以下进展记录，提取关键信息。返回 JSON 格式：
{
  "projectName": "项目名称",
  "summary": "一句话摘要",
  "tags": ["标签1", "标签2"]
}

进展内容：
${content}

注意：
- projectName 应该是简洁的项目标识（如果无法判断，返回"未分类项目"）
- summary 控制在 30 字以内
- tags 最多 3 个，选择最相关的`
        }]
      });

      const responseText = message.content[0].text;
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);

      if (jsonMatch) {
        const result = JSON.parse(jsonMatch[0]);
        return result;
      }

      throw new Error('AI response parsing failed');
    } catch (error) {
      console.error('AI analysis error:', error.message);
      // Fallback
      return {
        projectName: 'Default Project',
        summary: content.substring(0, 50) + '...',
        tags: ['general']
      };
    }
  }

  // 生成项目回顾提醒消息
  async generateReminderMessage(projectName, recentProgress) {
    if (!this.client) {
      return `${projectName} 已经 1 天没有更新了，今天要继续推进吗？`;
    }

    try {
      const progressSummary = recentProgress
        .map(p => `- ${p.ai_summary || p.content.substring(0, 50)}`)
        .join('\n');

      const message = await this.client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 200,
        messages: [{
          role: 'user',
          content: `项目"${projectName}"最近的进展：
${progressSummary}

请生成一条简短的提醒消息（不超过 50 字），问用户今天是否要继续推进这个项目。语气友好、简洁。`
        }]
      });

      return message.content[0].text.trim();
    } catch (error) {
      console.error('Reminder generation error:', error.message);
      return `${projectName} 已经 1 天没有更新了，今天要继续推进吗？`;
    }
  }

  // 生成确认消息
  getConfirmationMessage(projectName, summary) {
    return `已记录。${projectName} - ${summary}`;
  }
}

module.exports = new AIService();
