# 🌱 Seedling Tracker

一个简洁优雅的对话代理系统，具备记忆功能。

## ✨ 特性

- 💬 **智能对话**：基于模式匹配的对话代理
- 🧠 **记忆管理**：自动管理对话历史
- 🎨 **优雅界面**：Gradio 驱动的 Web UI
- ⚡ **零配置**：开箱即用，无需复杂设置

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 启动应用

```bash
python app.py
```

### 3️⃣ 打开浏览器

访问 `http://localhost:7860` 即可使用

## 📁 项目结构

```
seedling-tracker/
├── memory.py          # 记忆管理核心
├── agent.py           # 对话代理核心
├── app.py             # Gradio Web 界面
└── requirements.txt   # 依赖项
```

## 💡 可用命令

- `/help` - 显示帮助信息
- `/clear` - 清空对话记忆
- `/history` - 查看对话历史
- `/stats` - 查看统计信息

## 🛠️ 技术栈

- **Python 3.8+**
- **Gradio** - Web 界面框架

## 📝 设计哲学

- ✅ **简洁至上**：消除特殊情况，单一数据结构
- ✅ **实用主义**：解决真实问题，避免过度设计
- ✅ **可扩展性**：易于集成真实 LLM API