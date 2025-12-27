# Seedling Tracker - AI 进度追踪助手

> **🔴 重要规范：任何功能、架构、写法的更新，必须在工作结束后更新相关目录的子文档！**

## 项目简介

一个轻量级的 AI 进度追踪工具，帮助你记录任务进展、自动归类、智能提醒。

## MVP 功能

- ✅ 文字输入记录进展
- ✅ AI 自动理解和归类
- ✅ 定时提醒回顾
- ✅ 简单的进展列表展示

## 快速开始

```bash
# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 OpenAI/Claude API Key

# 初始化数据库
npm run db:init

# 启动服务
npm start

# 访问 http://localhost:3000
```

## 项目结构

```
seedling-tracker/
├── README.md                    # 👈 你在这里
├── docs/                        # 文档目录
│   └── architecture.md          # 架构设计文档
├── src/
│   ├── server/                  # 后端服务
│   │   ├── routes/              # API 路由
│   │   ├── services/            # 核心服务（AI、存储、定时任务）
│   │   └── db/                  # 数据库
│   └── client/                  # 前端界面
├── package.json
└── .env.example
```

## 技术栈

- **后端**：Node.js + Express + SQLite
- **前端**：原生 HTML/CSS/JavaScript
- **AI**：OpenAI API / Anthropic Claude API
- **定时任务**：node-cron

## 开发规范

### 📁 文件夹规范
每个文件夹必须包含 `README.md`，内容格式：
- 3 行以内的架构说明
- 列出每个文件的：名字、地位、功能

### 📄 文件规范
每个代码文件开头必须包含三行注释：
```javascript
// INPUT: 依赖外部的什么（API、模块、数据）
// OUTPUT: 对外提供什么（函数、接口、数据）
// POS: 在系统中的地位（核心/工具/配置等）
// ⚠️ 更新提醒：修改此文件后，务必更新文件开头注释和所属文件夹的 README.md
```

### 🔄 更新流程
1. 修改代码 → 更新文件开头注释
2. 文件夹变化 → 更新文件夹 README.md
3. 架构变化 → 更新 docs/architecture.md
4. 功能变化 → 更新根目录 README.md

## 详细文档

- [架构设计](./docs/architecture.md)
- [后端服务](./src/server/README.md)
- [前端界面](./src/client/README.md)

## License

MIT