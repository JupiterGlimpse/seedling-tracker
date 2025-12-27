-- INPUT: 无（SQL schema 定义文件）
-- OUTPUT: 数据库表结构（projects, progress_entries, reminders）
-- POS: 数据层核心配置，定义所有数据模型
-- ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md

-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active', -- active, paused, completed
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    remind_after DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 进展记录表
CREATE TABLE IF NOT EXISTS progress_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    ai_summary TEXT,
    tags TEXT, -- JSON array stored as string
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 提醒表
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    scheduled_time DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, sent, dismissed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_progress_project ON progress_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status, scheduled_time);
