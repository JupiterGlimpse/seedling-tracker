# Notion配置超简单指南 🚀

## 5分钟完成配置

### 步骤1: 创建Notion Integration（2分钟）

1. 访问 https://www.notion.so/my-integrations
2. 点击 **"+ New integration"**
3. 填写信息：
   - Name: `Job Tracker Bot`（随便起名）
   - Associated workspace: 选择你的workspace
   - Type: Internal
4. 点击 **Submit**
5. 复制 **Internal Integration Token**（格式：`secret_xxx...`）

### 步骤2: 创建Notion页面（1分钟）

1. 在Notion中创建新页面，命名为 **"AI PM求职追踪"**
2. 在页面右上角点击 **"..."** → **"Add connections"**
3. 搜索并选择你刚创建的Integration（`Job Tracker Bot`）
4. 点击确认授权

### 步骤3: 获取页面ID（1分钟）

打开刚创建的页面，看URL：
```
https://www.notion.so/AI-PM-xxxxxxxxxxxx?xxx
                           ^^^^^^^^^^^^^^^^
                           这就是Page ID
```

复制这32位字符（去掉问号后面的部分）

### 步骤4: 配置环境变量（1分钟）

创建 `.env` 文件：

```bash
# Notion配置
NOTION_API_KEY=secret_你的Token
NOTION_PAGE_ID=你的PageID

# Boss直聘配置（可选）
JOB_KEYWORD=AI产品经理
JOB_CITY=北京
```

## 完成！🎉

现在运行：
```bash
# 自动创建3个Database并测试
python3 test_job_automation.py
```

---

## Notion数据库结构预览

系统会自动创建3个Database：

### 📋 Jobs Database（职位库）
- 日期（Date）
- 公司（Title）
- 职位（Text）
- 薪资（Text）
- 城市（Select）
- JD（Text）
- 链接（URL）
- 匹配度（Number）
- 匹配原因（Text）
- 状态（Select）：新发现/待申请/已申请/已拒绝

### 📝 Applications Database（申请追踪）
- 公司（Relation → Jobs）
- 申请日期（Date）
- 打招呼话术（Text）
- 状态（Select）：待review/已发送/已回复/待follow-up
- HR回复（Text）
- 下次联系日期（Date）
- 备注（Text）

### 📊 Weekly Stats Database（周统计）
- 周数（Title）
- 新增职位（Number）
- 已申请（Number）
- 收到回复（Number）
- 回复率（Text）

---

## 优势对比

### ✅ Notion（推荐）
- 🚀 配置超简单（只需API key）
- 🎨 界面美观，可视化好
- 📱 支持移动端
- 🆓 免费版够用
- 🔄 实时同步
- 📊 多种视图（表格/看板/日历）

### ❌ Google Sheets（复杂）
- ⚠️ 需要创建服务账号
- ⚠️ 需要下载JSON凭据
- ⚠️ 需要共享表格权限
- ⚠️ 配置步骤多

---

## 常见问题

### Q: 找不到Integration Token？
A: 访问 https://www.notion.so/my-integrations，点击你的Integration即可看到Token

### Q: 提示"Page not found"？
A: 确保在页面中添加了Connection（步骤2第2-4步）

### Q: 如何查看数据？
A: 直接在Notion中打开"AI PM求职追踪"页面，所有数据实时可见

---

**就这么简单！开始使用吧 🎯**
