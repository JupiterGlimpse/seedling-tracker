# Seedling Tracker - 架构设计文档

> ⚠️ 一旦架构有所变化，请更新我。

## 整体架构

```
┌─────────────────────────────────────────┐
│          前端 (Client)                   │
│   输入框 | 进展列表 | 提醒面板            │
└─────────────────────────────────────────┘
                  ↓ HTTP
┌─────────────────────────────────────────┐
│          API 层 (Routes)                 │
│   POST /api/progress  | GET /api/reminders│
└─────────────────────────────────────────┘
                  ↓
┌──────────────┬──────────────┬───────────┐
│  AI Service  │  Storage     │ Scheduler │
│  理解+归类    │  数据持久化   │ 定时提醒  │
└──────────────┴──────────────┴───────────┘
                  ↓
┌─────────────────────────────────────────┐
│         SQLite 数据库                    │
│  projects | progress_entries | reminders│
└─────────────────────────────────────────┘
```

## 核心流程

### 1. 记录进展
1. 用户在前端输入文字
2. 前端 POST 到 `/api/progress`
3. 路由调用 AI Service 分析内容
4. AI 返回项目归类 + 摘要
5. Storage Service 保存到数据库
6. 返回 "已记录" 确认

### 2. 定时提醒
1. Scheduler 每小时检查一次
2. 查找 24 小时未更新的项目
3. AI Service 生成回顾摘要
4. 创建提醒记录
5. 前端轮询或 WebSocket 推送

### 3. 用户回复
1. 用户选择 [推进] 或 [搁置N天]
2. 更新项目状态和提醒时间
3. 如果推进，允许继续记录

## 数据模型

### projects (项目表)
- id: INTEGER PRIMARY KEY
- name: TEXT (项目名称)
- status: TEXT (active/paused/completed)
- last_update: DATETIME
- remind_after: DATETIME

### progress_entries (进展记录表)
- id: INTEGER PRIMARY KEY
- project_id: INTEGER
- content: TEXT (原始输入)
- ai_summary: TEXT (AI 摘要)
- tags: TEXT (JSON 数组)
- created_at: DATETIME

### reminders (提醒表)
- id: INTEGER PRIMARY KEY
- project_id: INTEGER
- message: TEXT
- scheduled_time: DATETIME
- status: TEXT (pending/sent/dismissed)

## 技术选型理由

- **SQLite**：轻量、零配置，适合个人工具
- **Express**：简单直接的 HTTP 服务器
- **原生 JS**：减少构建复杂度，快速启动
- **node-cron**：简单的定时任务，无需外部服务

## MVP 限制

- ❌ 不支持语音输入（需要额外 API 成本）
- ❌ 不支持文档上传（简化存储逻辑）
- ❌ 不支持多用户（单机版）
- ❌ 不支持复杂可视化（只有列表）

## 未来扩展

- 添加 WebSocket 实时推送
- 支持文档解析
- 添加进度图表
- 多用户支持
