# 快速开始指南 - AI PM求职自动化

## ⚡ 5分钟上手

### 1️⃣ 安装依赖

```bash
# 运行自动设置脚本
./setup.sh

# 或手动安装
pip install -r requirements.txt
```

### 2️⃣ 配置Google Sheets API（首次使用）

#### 快速步骤：

1. **访问**: https://console.cloud.google.com/
2. **创建项目** → 启用 "Google Sheets API"
3. **创建服务账号** → 下载JSON密钥
4. **重命名为** `credentials.json` 并放到项目根目录
5. **运行创建表格**:
   ```bash
   python3 -c "from job_sheets_manager import JobSheetsManager; m = JobSheetsManager(); m.create_job_tracking_sheets()"
   ```
6. **复制输出的表格ID** → 保存到`.env`文件:
   ```bash
   echo "SPREADSHEET_ID='你的表格ID'" >> .env
   ```
7. **在Google Sheets中共享表格** → 添加服务账号邮箱为编辑者
   - 邮箱在 `credentials.json` 的 `client_email` 字段

### 3️⃣ 运行测试

```bash
# 完整测试（包含爬虫+Google Sheets）
python3 test_job_automation.py
```

### 4️⃣ 每日使用

```bash
# 搜索"AI产品经理"职位并保存到Google Sheets
python3 daily_job_search.py

# 自定义搜索
python3 daily_job_search.py "Python开发" "深圳" 30
```

---

## 📁 项目结构

```
seedling-tracker/
├── boss_scraper.py          # Boss直聘爬虫
├── job_sheets_manager.py    # Google Sheets管理器
├── daily_job_search.py      # 每日自动化脚本
├── test_job_automation.py   # 测试脚本
├── boss-scraper-mcp/        # MCP Server（用于Claude/Cursor）
│   ├── index.js
│   └── package.json
├── requirements.txt         # Python依赖
├── .env.example             # 环境变量模板
└── credentials.json         # Google API凭据（需自行创建）
```

---

## 🎯 使用场景

### 场景1: 每日自动搜索职位

```bash
# 创建cron任务（Linux/macOS）
crontab -e

# 添加：每天上午10点自动运行
0 10 * * * cd /path/to/seedling-tracker && python3 daily_job_search.py
```

### 场景2: 在Claude Desktop中使用

1. 安装MCP Server依赖:
   ```bash
   cd boss-scraper-mcp
   npm install
   ```

2. 配置Claude Desktop（`~/Library/Application Support/Claude/claude_desktop_config.json`）:
   ```json
   {
     "mcpServers": {
       "boss-scraper": {
         "command": "node",
         "args": ["/绝对路径/seedling-tracker/boss-scraper-mcp/index.js"]
       }
     }
   }
   ```

3. 重启Claude Desktop，然后对话:
   ```
   帮我在Boss直聘上搜索"AI产品经理"，城市选北京
   ```

### 场景3: Python脚本集成

```python
from boss_scraper import BossJobScraper
from job_sheets_manager import JobSheetsManager

# 搜索职位
with BossJobScraper() as scraper:
    jobs = scraper.search_jobs('AI产品经理', '北京', max_results=20)

# 保存到Google Sheets
manager = JobSheetsManager()
manager.add_jobs(jobs)

# 查看结果
for job in manager.get_jobs(limit=5):
    print(f"{job['company']} - {job['title']} - {job['salary']}")
```

---

## 🔧 常见问题速查

### ❌ ChromeDriver错误

```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver
```

### ❌ Google Sheets认证失败

检查：
1. `credentials.json` 文件存在
2. Google Sheets API已启用
3. 表格已共享给服务账号邮箱

### ❌ Boss直聘返回空结果

可能需要登录，使用非headless模式:
```python
with BossJobScraper(headless=False) as scraper:
    # 浏览器窗口会打开，可以手动登录
    jobs = scraper.search_jobs(...)
```

---

## 📚 完整文档

详细配置和高级用法请查看:
- [JOB_AUTOMATION_README.md](JOB_AUTOMATION_README.md) - 完整文档
- [.env.example](.env.example) - 环境变量配置
- [mcp_config.example.json](mcp_config.example.json) - MCP配置示例

---

## 🆘 获取帮助

遇到问题？
1. 查看完整文档: `JOB_AUTOMATION_README.md`
2. 提交Issue: https://github.com/your-repo/issues
3. 检查环境配置: 运行 `./setup.sh` 查看诊断信息

---

**Happy Job Hunting! 🎯**
