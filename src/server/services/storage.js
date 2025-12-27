// INPUT: SQLite 数据库连接，schema.sql 定义的表结构
// OUTPUT: 数据操作接口（createProject, addProgress, getProjects, etc.）
// POS: 数据访问层，封装所有数据库操作，被 routes 和其他 services 调用
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, '../db/database.db');
const SCHEMA_PATH = path.join(__dirname, '../db/schema.sql');

class StorageService {
  constructor() {
    this.db = null;
  }

  // 初始化数据库
  async init() {
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(DB_PATH, (err) => {
        if (err) return reject(err);

        // 读取并执行 schema
        const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
        this.db.exec(schema, (err) => {
          if (err) return reject(err);
          console.log('✅ Database initialized');
          resolve();
        });
      });
    });
  }

  // 创建或获取项目
  async findOrCreateProject(name) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT * FROM projects WHERE name = ? AND status != ?',
        [name, 'completed'],
        (err, row) => {
          if (err) return reject(err);
          if (row) return resolve(row);

          // 创建新项目
          this.db.run(
            'INSERT INTO projects (name, status) VALUES (?, ?)',
            [name, 'active'],
            function(err) {
              if (err) return reject(err);
              resolve({ id: this.lastID, name, status: 'active' });
            }
          );
        }
      );
    });
  }

  // 添加进展记录
  async addProgress(projectId, content, aiSummary, tags = []) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO progress_entries (project_id, content, ai_summary, tags) VALUES (?, ?, ?, ?)',
        [projectId, content, aiSummary, JSON.stringify(tags)],
        function(err) {
          if (err) return reject(err);

          // 更新项目最后更新时间
          this.db.run(
            'UPDATE projects SET last_update = CURRENT_TIMESTAMP WHERE id = ?',
            [projectId]
          );

          resolve({ id: this.lastID, projectId, content, aiSummary, tags });
        }.bind(this)
      );
    });
  }

  // 获取所有活跃项目
  async getActiveProjects() {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM projects WHERE status = ? ORDER BY last_update DESC',
        ['active'],
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  // 获取项目的进展记录
  async getProgressByProject(projectId, limit = 10) {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM progress_entries WHERE project_id = ? ORDER BY created_at DESC LIMIT ?',
        [projectId, limit],
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows.map(row => ({
            ...row,
            tags: JSON.parse(row.tags || '[]')
          })));
        }
      );
    });
  }

  // 获取需要提醒的项目（24小时未更新）
  async getProjectsNeedingReminder() {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM projects
         WHERE status = 'active'
         AND (remind_after IS NULL OR remind_after <= datetime('now'))
         AND last_update <= datetime('now', '-1 day')`,
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  // 创建提醒
  async createReminder(projectId, message, scheduledTime) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO reminders (project_id, message, scheduled_time) VALUES (?, ?, ?)',
        [projectId, message, scheduledTime],
        function(err) {
          if (err) return reject(err);
          resolve({ id: this.lastID, projectId, message, scheduledTime });
        }
      );
    });
  }

  // 获取待发送的提醒
  async getPendingReminders() {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT r.*, p.name as project_name
         FROM reminders r
         JOIN projects p ON r.project_id = p.id
         WHERE r.status = 'pending'
         AND r.scheduled_time <= datetime('now')
         ORDER BY r.scheduled_time ASC`,
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  // 更新提醒状态
  async updateReminderStatus(reminderId, status) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'UPDATE reminders SET status = ? WHERE id = ?',
        [status, reminderId],
        (err) => {
          if (err) return reject(err);
          resolve();
        }
      );
    });
  }

  // 更新项目状态
  async updateProjectStatus(projectId, status, remindAfterDays = null) {
    return new Promise((resolve, reject) => {
      let query = 'UPDATE projects SET status = ?';
      const params = [status];

      if (remindAfterDays) {
        query += `, remind_after = datetime('now', '+${remindAfterDays} days')`;
      }

      query += ' WHERE id = ?';
      params.push(projectId);

      this.db.run(query, params, (err) => {
        if (err) return reject(err);
        resolve();
      });
    });
  }

  // 获取所有进展记录（用于前端展示）
  async getAllProgress(limit = 50) {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT pe.*, p.name as project_name, p.status as project_status
         FROM progress_entries pe
         JOIN projects p ON pe.project_id = p.id
         ORDER BY pe.created_at DESC
         LIMIT ?`,
        [limit],
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows.map(row => ({
            ...row,
            tags: JSON.parse(row.tags || '[]')
          })));
        }
      );
    });
  }
}

module.exports = new StorageService();
