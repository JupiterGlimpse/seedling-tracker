// INPUT: DOM 元素，后端 API（/api/progress, /api/reminders），用户交互事件
// OUTPUT: 动态更新的界面（进展列表、提醒、确认消息）
// POS: 前端核心逻辑，处理所有用户交互和 API 通信
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

class SeedlingTracker {
  constructor() {
    this.progressInput = document.getElementById('progress-input');
    this.submitBtn = document.getElementById('submit-btn');
    this.confirmationMsg = document.getElementById('confirmation-msg');
    this.progressList = document.getElementById('progress-list');
    this.refreshBtn = document.getElementById('refresh-btn');
    this.remindersPanel = document.getElementById('reminders-panel');

    this.init();
  }

  init() {
    // 绑定事件
    this.submitBtn.addEventListener('click', () => this.submitProgress());
    this.refreshBtn.addEventListener('click', () => this.loadProgress());
    this.progressInput.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        this.submitProgress();
      }
    });

    // 加载初始数据
    this.loadProgress();
    this.loadReminders();

    // 定期检查提醒（每 5 分钟）
    setInterval(() => this.loadReminders(), 5 * 60 * 1000);
  }

  // 提交进展记录
  async submitProgress() {
    const content = this.progressInput.value.trim();

    if (!content) {
      this.showConfirmation('请输入内容', 'error');
      return;
    }

    this.submitBtn.disabled = true;
    this.submitBtn.textContent = '记录中...';

    try {
      const response = await fetch('/api/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });

      const result = await response.json();

      if (result.success) {
        this.showConfirmation(result.message, 'success');
        this.progressInput.value = '';
        this.loadProgress();
      } else {
        this.showConfirmation('记录失败，请重试', 'error');
      }
    } catch (error) {
      console.error('Submit error:', error);
      this.showConfirmation('网络错误，请检查服务器', 'error');
    } finally {
      this.submitBtn.disabled = false;
      this.submitBtn.textContent = '记录';
    }
  }

  // 显示确认消息
  showConfirmation(message, type = 'success') {
    this.confirmationMsg.textContent = message;
    this.confirmationMsg.className = `confirmation-msg ${type}`;
    this.confirmationMsg.style.display = 'block';

    setTimeout(() => {
      this.confirmationMsg.style.display = 'none';
    }, 3000);
  }

  // 加载进展列表
  async loadProgress() {
    try {
      const response = await fetch('/api/progress?limit=20');
      const result = await response.json();

      if (result.success) {
        this.renderProgress(result.data);
      }
    } catch (error) {
      console.error('Load progress error:', error);
      this.progressList.innerHTML = '<p class="error">加载失败</p>';
    }
  }

  // 渲染进展列表
  renderProgress(progressList) {
    if (progressList.length === 0) {
      this.progressList.innerHTML = '<p class="empty">还没有任何记录，开始记录你的第一条进展吧！</p>';
      return;
    }

    this.progressList.innerHTML = progressList.map(item => `
      <div class="progress-item">
        <div class="progress-header">
          <span class="project-name">${this.escapeHtml(item.project_name)}</span>
          <span class="progress-time">${this.formatTime(item.created_at)}</span>
        </div>
        <div class="progress-summary">${this.escapeHtml(item.ai_summary || item.content)}</div>
        ${item.tags ? `
          <div class="progress-tags">
            ${JSON.parse(item.tags).map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join('')}
          </div>
        ` : ''}
        <details class="progress-details">
          <summary>查看原始内容</summary>
          <p>${this.escapeHtml(item.content)}</p>
        </details>
      </div>
    `).join('');
  }

  // 加载提醒
  async loadReminders() {
    try {
      const response = await fetch('/api/reminders');
      const result = await response.json();

      if (result.success && result.data.length > 0) {
        this.renderReminders(result.data);
      } else {
        this.remindersPanel.style.display = 'none';
      }
    } catch (error) {
      console.error('Load reminders error:', error);
    }
  }

  // 渲染提醒
  renderReminders(reminders) {
    this.remindersPanel.innerHTML = reminders.map(reminder => `
      <div class="reminder-item" data-id="${reminder.id}" data-project-id="${reminder.project_id}">
        <div class="reminder-icon">⏰</div>
        <div class="reminder-content">
          <strong>${this.escapeHtml(reminder.project_name)}</strong>
          <p>${this.escapeHtml(reminder.message)}</p>
        </div>
        <div class="reminder-actions">
          <button class="btn-proceed" onclick="app.respondReminder(${reminder.id}, 'proceed')">推进</button>
          <button class="btn-pause" onclick="app.respondReminder(${reminder.id}, 'pause', 3)">搁置3天</button>
          <button class="btn-dismiss" onclick="app.respondReminder(${reminder.id}, 'dismiss')">忽略</button>
        </div>
      </div>
    `).join('');

    this.remindersPanel.style.display = 'block';
  }

  // 响应提醒
  async respondReminder(reminderId, action, pauseDays = null) {
    try {
      const response = await fetch(`/api/reminders/${reminderId}/respond`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, pauseDays })
      });

      const result = await response.json();

      if (result.success) {
        // 移除该提醒
        const reminderElement = document.querySelector(`[data-id="${reminderId}"]`);
        if (reminderElement) {
          reminderElement.remove();
        }

        // 如果没有提醒了，隐藏面板
        if (this.remindersPanel.children.length === 0) {
          this.remindersPanel.style.display = 'none';
        }

        // 如果选择推进，聚焦到输入框
        if (action === 'proceed') {
          this.progressInput.focus();
          this.showConfirmation('太好了！继续记录你的进展吧', 'success');
        }
      }
    } catch (error) {
      console.error('Respond reminder error:', error);
    }
  }

  // 工具函数：转义 HTML
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // 工具函数：格式化时间
  formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // 小于 1 分钟
    if (diff < 60000) return '刚刚';

    // 小于 1 小时
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;

    // 小于 24 小时
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;

    // 小于 7 天
    if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`;

    // 超过 7 天，显示具体日期
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

// 初始化应用
const app = new SeedlingTracker();
