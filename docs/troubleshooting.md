# 故障排除指南

## 问题 1: AI 分析错误 403 Forbidden

### 原因
- Anthropic API Key 未配置或无效
- API Key 权限不足

### 解决方案

#### 选项 A：使用 Mock 模式（无需 API Key）
系统已自动降级到 Mock 模式，可以正常使用基础功能。

Mock 模式特点：
- ✅ 自动提取第一个关键词作为项目名称
- ✅ 保留原文前 50 字作为摘要
- ✅ 提取前 3 个关键词作为标签
- ⚠️ 没有 AI 智能分析

#### 选项 B：配置 Anthropic API Key（推荐）
1. 访问 https://console.anthropic.com/
2. 创建 API Key
3. 编辑 `.env` 文件：
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. 重启服务器

## 问题 2: Gallery 无法刷新

### 可能原因
1. 服务器未启动
2. 数据库未初始化
3. API 路由错误

### 解决方案

#### 1. 检查服务器状态
打开浏览器访问：http://localhost:3000/api/health

如果返回 `{"status":"ok",...}`，说明服务器正常运行。

#### 2. 重新初始化数据库
```bash
npm run db:init
```

#### 3. 完全重启
```bash
# 停止当前服务器（Ctrl+C）
# 重新启动
npm start
```

#### 4. 使用快速启动脚本
```bash
./start.sh
```

## 快速测试流程

1. **启动服务器**
   ```bash
   npm start
   ```

2. **打开浏览器**
   访问 http://localhost:3000

3. **记录第一条进展**
   输入任意内容，点击"记录"

4. **检查结果**
   - 应该显示"已记录"确认消息
   - Gallery 中应该出现记录
   - 如果使用 Mock 模式，会有提示

## 常见问题

### Q: 为什么显示"Mock 模式"？
A: 没有配置 AI API Key，系统自动使用简化的分析模式。功能正常，只是分析不够智能。

### Q: 如何获取 API Key？
A: 访问 https://console.anthropic.com/ 注册并创建 API Key。

### Q: Mock 模式够用吗？
A: 对于基础使用足够。如需智能分析、自动归类、生成提醒消息等高级功能，建议配置 API Key。

### Q: Gallery 一直显示"加载中"？
A:
1. 检查浏览器控制台（F12）查看错误信息
2. 确认服务器正在运行
3. 尝试刷新页面

## 开发者调试

### 查看服务器日志
服务器会输出详细的状态信息：
- ✅ 成功操作
- 🔄 Mock 模式切换
- ⚠️ 警告信息
- ❌ 错误信息

### 常见日志信息

```
🔄 Using mock mode for AI analysis
```
→ 正常：使用 Mock 模式

```
⚠️  API Access Forbidden (403)
🔄 Falling back to mock mode
```
→ API Key 问题，已降级到 Mock 模式

```
✅ Database initialized
✅ AI Service initialized (Anthropic)
```
→ 完美：所有服务正常启动

## 需要帮助？

如问题仍未解决：
1. 查看服务器终端输出
2. 检查浏览器控制台（F12）
3. 提交 Issue: https://github.com/JupiterGlimpse/seedling-tracker/issues
