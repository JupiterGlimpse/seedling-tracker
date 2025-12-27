# db - 数据库层

> ⚠️ 一旦我所属的文件夹有所变化，请更新我。

## 架构说明
使用 SQLite 作为嵌入式数据库，存储项目、进展记录、提醒等数据。
schema.sql 定义表结构，由 storage 服务初始化和使用。

## 文件列表

| 名称 | 地位 | 功能 |
|------|------|------|
| `schema.sql` | 配置 | 定义数据库表结构（projects, progress_entries, reminders） |
| `database.db` | 数据 | SQLite 数据库文件（运行时生成，不提交到 git） |
