# server - 后端服务

> ⚠️ 一旦我所属的文件夹有所变化，请更新我。

## 架构说明
Express 服务器，提供 RESTful API。
routes 处理 HTTP 请求，services 处理业务逻辑，db 管理数据存储。
启动时初始化数据库和定时任务。

## 文件/文件夹列表

| 名称 | 地位 | 功能 |
|------|------|------|
| `index.js` | 入口 | 启动 Express 服务器，注册路由和中间件 |
| `routes/` | 路由层 | 处理 HTTP 请求，调用 services 处理业务 |
| `services/` | 业务层 | 核心业务逻辑：AI 分析、数据存储、定时任务 |
| `db/` | 数据层 | 数据库 schema 和连接管理 |
