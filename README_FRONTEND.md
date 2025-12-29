# Memory Agent 前端界面

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并添加你的 OpenAI API Key:

```
OPENAI_API_KEY=your_api_key_here
```

### 3. 启动服务器

```bash
python app.py
```

### 4. 访问界面

在浏览器中打开: http://localhost:5000

## 功能说明

### 前端界面 (index.html)
- 简洁的聊天界面
- 实时消息发送和接收
- 加载动画和错误提示
- 响应式设计

### 后端 API (app.py)
- `POST /chat` - 发送消息并获取回复
- `GET /memories` - 搜索历史记忆
- `GET /health` - 健康检查

## 架构说明

```
前端 (HTML/JS)
    ↓
Flask API (app.py)
    ↓
MemoryAgent (agent.py)
    ↓
MemorySystem (memory.py)
    ↓
ChromaDB + OpenAI
```

## 优势

1. **最小改动** - 不修改原有的 agent.py 和 memory.py
2. **性能优秀** - Flask 轻量级，单页面应用
3. **部署简单** - 只需一个命令即可启动
4. **易于扩展** - 可轻松添加新的 API 端点

## 测试建议

1. 发送简单消息测试基本对话
2. 发送相关联的消息测试记忆检索
3. 刷新页面后继续对话，验证持久化存储

## 注意事项

- 确保 OpenAI API Key 已正确配置
- ChromaDB 数据存储在内存中，重启服务器会丢失
- 如需持久化，可修改 memory.py 使用磁盘存储
