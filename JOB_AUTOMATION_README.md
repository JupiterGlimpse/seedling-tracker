# AI PM 求职自动化系统

基于Google Sheets的智能求职追踪系统，自动抓取Boss直聘职位信息并管理求职流程。

## 📋 目录

- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [Google Sheets配置](#google-sheets配置)
- [使用方法](#使用方法)
- [MCP Server配置](#mcp-server配置)
- [常见问题](#常见问题)

---

## 🏗️ 系统架构

### 组件说明

1. **Boss直聘爬虫** (`boss_scraper.py`)
   - Python + Selenium实现
   - 支持关键词、城市、经验筛选
   - 自动提取职位详细信息

2. **Google Sheets管理器** (`job_sheets_manager.py`)
   - 自动创建和管理3个Sheet页面
   - Jobs（职位库）、Applications（申请追踪）、WeeklyStats（周统计）
   - 提供数据读写、统计分析功能

3. **MCP Server** (`boss-scraper-mcp/`)
   - Node.js + Puppeteer实现
   - 可集成到Claude Desktop/Cursor
   - 通过stdio协议提供工具接口

### Google Sheets表结构

#### Jobs表（职位库）
| 列 | 字段 | 说明 |
|----|------|------|
| A | 日期 | 发现日期 |
| B | 公司 | 公司名称 |
| C | 职位 | 职位名称 |
| D | 薪资 | 薪资范围 |
| E | 城市 | 工作地点 |
| F | JD | 职位描述（前200字） |
| G | 链接 | Boss直聘链接 |
| H | 匹配度 | 0-100分 |
| I | 匹配原因 | 为什么匹配 |
| J | 状态 | 新发现/待申请/已申请/已拒绝 |

#### Applications表（申请追踪）
| 列 | 字段 | 说明 |
|----|------|------|
| A | 公司 | 关联Jobs |
| B | 申请日期 | |
| C | 打招呼话术 | 生成的开场白 |
| D | 状态 | 待review/已发送/已回复/待follow-up |
| E | HR回复 | 记录对话 |
| F | 下次联系日期 | |
| G | 备注 | |

#### WeeklyStats表（周统计）
| 列 | 字段 | 说明 |
|----|------|------|
| A | 周数 | 第X周 |
| B | 新增职位 | |
| C | 已申请 | |
| D | 收到回复 | |
| E | 回复率 | |

---

## 🚀 快速开始

### 1. 安装Python依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Chrome浏览器和ChromeDriver
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver

# macOS
brew install chromedriver
```

### 2. 运行测试

```bash
# 运行完整测试（包含爬虫和Google Sheets）
python test_job_automation.py

# 仅测试爬虫
python boss_scraper.py
```

---

## 🔑 Google Sheets配置

### 步骤1: 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 在"API和服务"中启用 **Google Sheets API**

### 步骤2: 创建服务账号

1. 进入"凭据"页面
2. 点击"创建凭据" → "服务账号"
3. 填写服务账号名称（如：`job-tracker-bot`）
4. 授予角色：**编辑者**
5. 完成创建

### 步骤3: 下载密钥文件

1. 在服务账号列表中，点击刚创建的账号
2. 切换到"密钥"标签
3. 点击"添加密钥" → "创建新密钥"
4. 选择JSON格式
5. **下载并重命名为 `credentials.json`**
6. 将文件放在项目根目录

### 步骤4: 创建并配置Google Sheets

```bash
# 运行管理器创建新表格
python -c "from job_sheets_manager import JobSheetsManager; m = JobSheetsManager(); m.create_job_tracking_sheets()"
```

创建后会输出表格ID，例如：
```
表格ID: 1a2b3c4d5e6f7g8h9i0j
URL: https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j
```

### 步骤5: 共享表格给服务账号

1. 打开创建的Google Sheets
2. 点击右上角"共享"
3. **重要**: 将`credentials.json`中的`client_email`地址添加为编辑者
   - 示例：`job-tracker-bot@project-id.iam.gserviceaccount.com`
4. 点击"发送"

### 步骤6: 设置环境变量

```bash
# Linux/macOS
export SPREADSHEET_ID='1a2b3c4d5e6f7g8h9i0j'
export GOOGLE_CREDENTIALS_PATH='credentials.json'

# Windows (PowerShell)
$env:SPREADSHEET_ID='1a2b3c4d5e6f7g8h9i0j'
$env:GOOGLE_CREDENTIALS_PATH='credentials.json'

# 永久保存（添加到 ~/.bashrc 或 ~/.zshrc）
echo "export SPREADSHEET_ID='1a2b3c4d5e6f7g8h9i0j'" >> ~/.bashrc
echo "export GOOGLE_CREDENTIALS_PATH='$(pwd)/credentials.json'" >> ~/.bashrc
source ~/.bashrc
```

---

## 📖 使用方法

### Python脚本方式

#### 1. 搜索并保存职位

```python
from boss_scraper import BossJobScraper
from job_sheets_manager import JobSheetsManager

# 搜索职位
with BossJobScraper(headless=True) as scraper:
    jobs = scraper.search_jobs(
        keyword='AI产品经理',
        city='北京',
        page=1,
        max_results=20
    )

# 保存到Google Sheets
manager = JobSheetsManager()
manager.add_jobs(jobs)

# 查看前5个职位
saved_jobs = manager.get_jobs(limit=5)
for i, job in enumerate(saved_jobs, 1):
    print(f"{i}. {job['company']} - {job['title']} - {job['salary']}")
```

#### 2. 添加申请记录

```python
manager = JobSheetsManager()
manager.add_application(
    company='字节跳动',
    greeting='您好，我对贵司的AI产品经理职位很感兴趣...',
    status='待review'
)
```

#### 3. 更新周统计

```python
manager = JobSheetsManager()
manager.update_weekly_stats()
```

### 命令行快速使用

```bash
# 测试爬虫（显示前5个职位）
python boss_scraper.py

# 完整流程测试
python test_job_automation.py
```

---

## 🔧 MCP Server配置

MCP Server允许在Claude Desktop或Cursor中使用Boss直聘爬虫。

### 1. 安装Node.js依赖

```bash
cd boss-scraper-mcp
npm install
```

### 2. 测试MCP Server

```bash
# 直接运行测试
node index.js
```

### 3. 配置Claude Desktop

编辑Claude Desktop配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "boss-scraper": {
      "command": "node",
      "args": ["/绝对路径/seedling-tracker/boss-scraper-mcp/index.js"]
    },
    "google-sheets": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"]
    }
  }
}
```

**重要**: 替换 `/绝对路径/` 为实际的完整路径！

### 4. 配置Cursor

编辑Cursor配置文件：

**macOS/Linux**: `~/.cursor/mcp_config.json`
**Windows**: `%USERPROFILE%\.cursor\mcp_config.json`

使用相同的配置格式。

### 5. 在Claude/Cursor中使用

重启Claude Desktop或Cursor后，可以直接对话：

```
帮我在Boss直聘上搜索"AI产品经理"职位，城市选北京
```

Claude会自动调用MCP工具并返回结果。

---

## 🔍 常见问题

### Q1: Selenium提示找不到ChromeDriver

**解决方法**:
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# 手动下载
# 访问 https://chromedriver.chromium.org/downloads
# 下载对应Chrome版本的driver
# 解压后放到PATH目录（如 /usr/local/bin）
```

### Q2: Boss直聘返回空结果或需要登录

**原因**: Boss直聘有反爬虫机制，可能需要登录。

**解决方法**:
1. 使用 `headless=False` 打开浏览器窗口
2. 手动登录后脚本会继续执行
3. 或考虑使用官方API（如果有）

```python
with BossJobScraper(headless=False) as scraper:
    # 会打开浏览器窗口，可以手动操作
    jobs = scraper.search_jobs(...)
```

### Q3: Google Sheets API认证失败

**检查清单**:
- [ ] `credentials.json` 文件存在且格式正确
- [ ] Google Sheets API已在Cloud Console中启用
- [ ] 表格已共享给服务账号邮箱（`client_email`）
- [ ] 环境变量 `SPREADSHEET_ID` 已设置

### Q4: MCP Server无法连接

**检查**:
1. Node.js版本 >= 16
2. 依赖已安装：`cd boss-scraper-mcp && npm install`
3. 配置文件中的路径是**绝对路径**
4. 重启Claude Desktop/Cursor

### Q5: 如何自动化运行？

**使用cron定时任务** (Linux/macOS):

```bash
# 编辑crontab
crontab -e

# 每天上午10点运行
0 10 * * * cd /path/to/seedling-tracker && /usr/bin/python3 test_job_automation.py >> /tmp/job-automation.log 2>&1
```

**使用Windows任务计划程序**:
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天10:00）
4. 操作：启动程序 → `python.exe`
5. 参数：`test_job_automation.py`
6. 起始于：项目目录

---

## 📊 使用示例

### 完整求职流程

```python
#!/usr/bin/env python3
from boss_scraper import BossJobScraper
from job_sheets_manager import JobSheetsManager

def daily_job_search():
    """每日求职自动化流程"""

    # 1. 搜索职位
    print("🔍 正在搜索职位...")
    with BossJobScraper(headless=True) as scraper:
        jobs = scraper.search_jobs(
            keyword='AI产品经理',
            city='北京',
            page=1,
            max_results=20
        )

    if not jobs:
        print("未找到新职位")
        return

    print(f"✓ 找到 {len(jobs)} 个职位")

    # 2. 保存到Google Sheets
    print("💾 正在保存到Google Sheets...")
    manager = JobSheetsManager()
    manager.add_jobs(jobs)

    # 3. 更新周统计
    print("📊 正在更新统计...")
    manager.update_weekly_stats()

    # 4. 显示高匹配度职位
    print("\n📌 推荐职位（可手动标记匹配度后筛选）:")
    for job in jobs[:5]:
        print(f"  • {job['company']} - {job['title']}")
        print(f"    {job['salary']} | {job['location']}")
        print(f"    {job['url']}\n")

    print("✅ 完成!")

if __name__ == '__main__':
    daily_job_search()
```

---

## 🛠️ 高级配置

### 自定义城市代码

在 `boss_scraper.py` 中添加更多城市：

```python
CITY_CODES = {
    '北京': '101010100',
    '上海': '101020100',
    '杭州': '101210100',
    # 添加更多城市...
}
```

### AI匹配度评分（未来功能）

可以集成Claude API来自动评估职位匹配度：

```python
import anthropic

def calculate_match_score(job, resume):
    """使用Claude评估职位匹配度"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""
    根据以下简历和职位信息，评估匹配度（0-100分）：

    简历：{resume}

    职位：{job['title']}
    公司：{job['company']}
    要求：{job['jd']}

    返回JSON格式：{{"score": 85, "reason": "匹配原因"}}
    """

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # 解析返回的JSON
    # ...
```

---

## 📝 开发路线图

- [x] Boss直聘基础爬虫
- [x] Google Sheets集成
- [x] MCP Server实现
- [ ] AI匹配度评分
- [ ] 自动生成打招呼话术
- [ ] 邮件/微信提醒
- [ ] 多平台支持（拉勾、LinkedIn）
- [ ] Web可视化界面

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📧 联系方式

如有问题，请提交GitHub Issue。
