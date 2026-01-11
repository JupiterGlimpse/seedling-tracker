# AI PM 求职自动化系统（Notion版 - 推荐） 🚀

基于Notion的智能求职追踪系统，**配置超简单**，只需5分钟！

## ⚡ 为什么选择Notion版？

### ✅ Notion（推荐）
- 🚀 **配置超简单**（只需2个环境变量）
- ⏱️ **5分钟上手**（不需要下载凭据文件）
- 🎨 **界面美观**（可视化好，支持多种视图）
- 📱 **移动端支持**（随时随地查看）
- 🆓 **免费够用**（个人版完全够用）
- 🔄 **实时同步**（多设备自动同步）

### ❌ Google Sheets（复杂）
- ⚠️ 需要创建Google Cloud项目
- ⚠️ 需要启用API
- ⚠️ 需要创建服务账号
- ⚠️ 需要下载JSON凭据文件
- ⚠️ 需要共享表格权限
- ⚠️ 配置步骤多达6-7步

---

## 🎯 快速开始（5分钟）

### 步骤1: 安装依赖（1分钟）

```bash
pip install -r requirements.txt
```

主要依赖：
- `notion-client` - Notion API
- `selenium` - Boss直聘爬虫
- `python-dotenv` - 环境变量管理

### 步骤2: 配置Notion（3分钟）

#### 2.1 创建Integration

1. 访问 https://www.notion.so/my-integrations
2. 点击 **"+ New integration"**
3. 填写名称（如：`Job Tracker Bot`）
4. 点击 **Submit**
5. 复制 **Internal Integration Token**（`secret_xxx...`）

#### 2.2 创建Notion页面

1. 在Notion中创建新页面，命名为 **"AI PM求职追踪"**
2. 点击页面右上角 **"..."** → **"Add connections"**
3. 选择刚创建的Integration
4. 复制页面URL中的**32位ID**
   ```
   https://www.notion.so/AI-PM-xxxxxxxxxxxx?xxx
                              ^^^^^^^^^^^^^^^^
                              这就是Page ID
   ```

#### 2.3 配置环境变量

创建 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑.env文件，填入：
NOTION_API_KEY=secret_你的Token
NOTION_PAGE_ID=你的32位ID
```

**就这么简单！✨**

### 步骤3: 运行测试（1分钟）

```bash
# 测试完整流程
python3 test_notion_automation.py
```

这会：
- 测试Boss直聘爬虫
- 自动创建3个Notion数据库
- 保存职位到Notion
- 显示前5个职位

---

## 📊 Notion数据库结构

系统会自动创建3个精美的Database：

### 📋 Jobs Database（职位库）
完整的职位信息，支持筛选、排序、多种视图：
- 📅 日期
- 🏢 公司（Title）
- 💼 职位
- 💰 薪资
- 📍 城市（Select - 支持筛选）
- 📝 JD
- 🔗 链接（可点击）
- 📊 匹配度（数字）
- 💡 匹配原因
- 🏷️ 状态（Select）：新发现/待申请/已申请/已拒绝

### 📝 Applications Database（申请追踪）
管理申请进度和HR沟通：
- 🏢 公司
- 📅 申请日期
- 💬 打招呼话术
- 🏷️ 状态：待review/已发送/已回复/待follow-up
- 💭 HR回复
- ⏰ 下次联系日期
- 📝 备注

### 📊 Weekly Stats Database（周统计）
自动统计求职数据：
- 📅 周数
- ➕ 新增职位
- 📤 已申请
- 📥 收到回复
- 📈 回复率

---

## 🎮 使用方法

### 方法1: 每日自动化脚本（推荐）

```bash
# 使用默认配置（AI产品经理 - 北京）
python3 daily_job_search_notion.py

# 自定义搜索
python3 daily_job_search_notion.py "Python开发" "深圳" 30
#                                  ↑关键词    ↑城市  ↑数量
```

### 方法2: Python脚本集成

```python
from boss_scraper import BossJobScraper
from notion_manager import NotionJobManager

# 搜索职位
with BossJobScraper() as scraper:
    jobs = scraper.search_jobs('AI产品经理', '北京', max_results=20)

# 保存到Notion
manager = NotionJobManager()

# 首次使用需要创建数据库
if not os.getenv('NOTION_JOBS_DB_ID'):
    manager.setup_databases()

# 添加职位
manager.add_jobs(jobs)

# 查看结果（直接在Notion中查看更方便！）
```

### 方法3: 定时自动运行

```bash
# Linux/macOS - 使用cron
crontab -e

# 每天上午10点自动运行
0 10 * * * cd /path/to/seedling-tracker && /usr/bin/python3 daily_job_search_notion.py
```

---

## 📁 项目文件说明

### 核心文件
```
seedling-tracker/
├── notion_manager.py              # Notion数据库管理器 ⭐
├── boss_scraper.py                # Boss直聘爬虫
├── daily_job_search_notion.py     # 每日自动化脚本 ⭐
├── test_notion_automation.py      # 测试脚本 ⭐
├── NOTION_SETUP.md                # Notion配置详细教程
├── .env.example                   # 环境变量模板
└── requirements.txt               # Python依赖

├── boss-scraper-mcp/              # MCP Server（可选）
│   ├── index.js
│   └── package.json

# Google Sheets版本（备用）
├── job_sheets_manager.py          # Google Sheets管理器
├── test_job_automation.py         # Google Sheets测试
└── JOB_AUTOMATION_README.md       # Google Sheets文档
```

---

## 🎨 Notion使用技巧

### 创建不同视图

在Notion中，你可以为Jobs数据库创建多种视图：

1. **📋 表格视图**（默认）
   - 查看所有职位详情

2. **📊 看板视图**
   - 按"状态"分组（新发现/待申请/已申请/已拒绝）
   - 拖拽卡片更新状态

3. **📍 城市视图**
   - 按"城市"分组
   - 快速查看不同城市的职位

4. **⭐ 高匹配度视图**
   - 筛选：匹配度 >= 70
   - 排序：按匹配度降序

### 批量操作

- ✅ 批量选择职位 → 更新状态
- 🏷️ 批量添加标签
- 📤 导出为CSV/PDF

---

## ❓ 常见问题

### Q1: 找不到Integration Token？
**A:** 访问 https://www.notion.so/my-integrations，点击你的Integration即可看到Token

### Q2: 提示"Page not found"或"object not found"？
**A:** 确保在Notion页面中添加了Connection：
1. 打开页面
2. 点击右上角 **"..."** → **"Add connections"**
3. 选择你的Integration

### Q3: 如何查看保存的职位？
**A:** 直接在Notion中打开"AI PM求职追踪"页面，所有数据实时可见！

### Q4: ChromeDriver错误？
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver
```

### Q5: Boss直聘返回空结果？
**A:** 可能需要登录，使用非headless模式：
```python
with BossJobScraper(headless=False) as scraper:
    # 会打开浏览器，可以手动登录
    jobs = scraper.search_jobs(...)
```

---

## 🚀 高级功能（可选）

### 1. AI匹配度评分

可以集成Claude API自动评估职位匹配度（需要ANTHROPIC_API_KEY）

### 2. 自动生成打招呼话术

基于职位JD和个人简历生成个性化开场白

### 3. MCP Server集成

在Claude Desktop/Cursor中使用：

```bash
cd boss-scraper-mcp
npm install

# 配置Claude Desktop
# 参考 JOB_AUTOMATION_README.md
```

---

## 📸 效果预览

### Notion数据库示例

**Jobs Database（职位库）**
```
📋 表格视图
┌────────────┬──────────┬──────────────┬────────┬────┬─────────┐
│ 公司       │ 职位     │ 薪资         │ 城市   │匹配│ 状态    │
├────────────┼──────────┼──────────────┼────────┼────┼─────────┤
│ 字节跳动   │AI产品经理│ 40-60K·15薪  │ 北京   │ 85 │ 待申请  │
│ 阿里巴巴   │AI PM     │ 35-55K·16薪  │ 杭州   │ 78 │ 新发现  │
│ 腾讯       │产品专家  │ 38-58K·14薪  │ 深圳   │ 82 │ 已申请  │
└────────────┴──────────┴──────────────┴────────┴────┴─────────┘
```

**看板视图（按状态）**
```
新发现          待申请          已申请          已拒绝
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 阿里    │    │ 字节    │    │ 腾讯    │    │         │
│ AI PM   │    │ AI产品  │    │ 产品专家│    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## 🎯 完整工作流程示例

### Day 1: 搜索职位
```bash
python3 daily_job_search_notion.py
```
→ 20个职位自动保存到Notion

### Day 2-3: 筛选和申请
1. 在Notion中打开"Jobs"数据库
2. 创建"高匹配度"视图（筛选 匹配度>=70）
3. 手动评估职位，更新匹配度和匹配原因
4. 将感兴趣的职位状态改为"待申请"

### Day 4-5: 发送申请
1. 在"Applications"数据库中添加记录
2. 填写公司名、打招呼话术
3. 发送后更新状态为"已发送"

### Day 6-7: 跟进
1. HR回复后，在"Applications"中记录回复内容
2. 更新状态为"已回复"
3. 设置"下次联系日期"提醒

### 周末: 查看统计
查看"Weekly Stats"数据库，分析：
- 本周新增了多少职位？
- 申请了多少个？
- 收到多少回复？
- 回复率是多少？

---

## 💡 最佳实践

1. **每天早上运行一次**
   ```bash
   python3 daily_job_search_notion.py
   ```

2. **及时更新状态**
   - 在Notion中拖拽卡片更新状态
   - 记录HR沟通内容

3. **定期review**
   - 每周查看统计数据
   - 调整搜索策略

4. **备份数据**
   - Notion支持导出为CSV/Markdown
   - 定期导出备份

---

## 🎉 总结

### 优势
- ✅ 配置简单（5分钟）
- ✅ 界面美观（Notion UI）
- ✅ 功能强大（多视图、筛选、排序）
- ✅ 移动支持（iOS/Android App）
- ✅ 免费够用（个人版）

### 下一步
1. 运行 `python3 test_notion_automation.py` 测试
2. 配置定时任务自动运行
3. 在Notion中个性化你的数据库
4. 开始你的求职之旅！🚀

---

**Happy Job Hunting! 🎯**

有问题？查看 [NOTION_SETUP.md](NOTION_SETUP.md) 获取详细配置教程
