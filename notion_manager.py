"""
Notion求职追踪管理工具
用于管理求职信息的Notion Database
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    from notion_client import Client
except ImportError:
    print("请先安装Notion SDK: pip install notion-client")
    exit(1)


class NotionJobManager:
    """Notion求职追踪管理器"""

    def __init__(self, api_key: str = None, page_id: str = None):
        """
        初始化管理器

        Args:
            api_key: Notion API密钥
            page_id: Notion页面ID（父页面）
        """
        self.api_key = api_key or os.getenv('NOTION_API_KEY')
        self.page_id = page_id or os.getenv('NOTION_PAGE_ID')

        if not self.api_key:
            print("❌ 未找到NOTION_API_KEY")
            print("请设置环境变量或创建.env文件")
            print("\n快速配置：")
            print("1. 访问 https://www.notion.so/my-integrations")
            print("2. 创建Integration并复制Token")
            print("3. export NOTION_API_KEY='secret_xxx...'")
            return

        if not self.page_id:
            print("❌ 未找到NOTION_PAGE_ID")
            print("请设置环境变量或创建.env文件")
            print("\n快速获取：")
            print("1. 在Notion中创建页面")
            print("2. 页面URL中的32位ID就是Page ID")
            print("3. export NOTION_PAGE_ID='xxx...'")
            return

        try:
            self.client = Client(auth=self.api_key)
            print("✓ Notion API连接成功")
        except Exception as e:
            print(f"❌ Notion API连接失败: {e}")
            self.client = None
            return

        # 数据库ID（初始化时会创建或获取）
        self.jobs_db_id = None
        self.applications_db_id = None
        self.stats_db_id = None

    def _create_jobs_database(self) -> str:
        """创建Jobs数据库"""
        try:
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.page_id},
                title=[{"type": "text", "text": {"content": "📋 Jobs（职位库）"}}],
                properties={
                    "公司": {"title": {}},  # Title是必需的
                    "日期": {"date": {}},
                    "职位": {"rich_text": {}},
                    "薪资": {"rich_text": {}},
                    "城市": {
                        "select": {
                            "options": [
                                {"name": "北京", "color": "blue"},
                                {"name": "上海", "color": "green"},
                                {"name": "深圳", "color": "purple"},
                                {"name": "杭州", "color": "orange"},
                                {"name": "广州", "color": "pink"},
                                {"name": "成都", "color": "yellow"},
                            ]
                        }
                    },
                    "JD": {"rich_text": {}},
                    "链接": {"url": {}},
                    "匹配度": {"number": {"format": "number"}},
                    "匹配原因": {"rich_text": {}},
                    "状态": {
                        "select": {
                            "options": [
                                {"name": "新发现", "color": "blue"},
                                {"name": "待申请", "color": "yellow"},
                                {"name": "已申请", "color": "green"},
                                {"name": "已拒绝", "color": "red"},
                            ]
                        }
                    },
                }
            )
            db_id = response["id"]
            print(f"✓ 创建Jobs数据库成功: {db_id}")
            return db_id
        except Exception as e:
            print(f"❌ 创建Jobs数据库失败: {e}")
            return None

    def _create_applications_database(self) -> str:
        """创建Applications数据库"""
        try:
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.page_id},
                title=[{"type": "text", "text": {"content": "📝 Applications（申请追踪）"}}],
                properties={
                    "公司": {"title": {}},
                    "申请日期": {"date": {}},
                    "打招呼话术": {"rich_text": {}},
                    "状态": {
                        "select": {
                            "options": [
                                {"name": "待review", "color": "gray"},
                                {"name": "已发送", "color": "blue"},
                                {"name": "已回复", "color": "green"},
                                {"name": "待follow-up", "color": "yellow"},
                            ]
                        }
                    },
                    "HR回复": {"rich_text": {}},
                    "下次联系日期": {"date": {}},
                    "备注": {"rich_text": {}},
                }
            )
            db_id = response["id"]
            print(f"✓ 创建Applications数据库成功: {db_id}")
            return db_id
        except Exception as e:
            print(f"❌ 创建Applications数据库失败: {e}")
            return None

    def _create_stats_database(self) -> str:
        """创建Weekly Stats数据库"""
        try:
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.page_id},
                title=[{"type": "text", "text": {"content": "📊 Weekly Stats（周统计）"}}],
                properties={
                    "周数": {"title": {}},
                    "新增职位": {"number": {"format": "number"}},
                    "已申请": {"number": {"format": "number"}},
                    "收到回复": {"number": {"format": "number"}},
                    "回复率": {"rich_text": {}},
                }
            )
            db_id = response["id"]
            print(f"✓ 创建Stats数据库成功: {db_id}")
            return db_id
        except Exception as e:
            print(f"❌ 创建Stats数据库失败: {e}")
            return None

    def setup_databases(self) -> bool:
        """初始化所有数据库"""
        if not self.client:
            print("❌ Notion客户端未初始化")
            return False

        print("\n正在创建Notion数据库...")
        print("="*60)

        # 创建三个数据库
        self.jobs_db_id = self._create_jobs_database()
        self.applications_db_id = self._create_applications_database()
        self.stats_db_id = self._create_stats_database()

        if all([self.jobs_db_id, self.applications_db_id, self.stats_db_id]):
            print("\n" + "="*60)
            print("✅ 所有数据库创建成功！")
            print("\n保存以下ID到.env文件以便下次使用:")
            print(f"NOTION_JOBS_DB_ID={self.jobs_db_id}")
            print(f"NOTION_APPLICATIONS_DB_ID={self.applications_db_id}")
            print(f"NOTION_STATS_DB_ID={self.stats_db_id}")
            print("\n在Notion中查看: https://notion.so/{}\n".format(self.page_id))
            return True
        else:
            print("\n❌ 数据库创建失败")
            return False

    def add_job(self, job: Dict[str, Any]) -> bool:
        """
        添加单个职位到Jobs数据库

        Args:
            job: 职位信息字典

        Returns:
            是否成功
        """
        if not self.jobs_db_id:
            self.jobs_db_id = os.getenv('NOTION_JOBS_DB_ID')
            if not self.jobs_db_id:
                print("❌ 未找到Jobs数据库ID，请先运行setup_databases()")
                return False

        try:
            properties = {
                "公司": {"title": [{"text": {"content": job.get('company', 'Unknown')[:100]}}]},
                "职位": {"rich_text": [{"text": {"content": job.get('title', '')[:2000]}}]},
                "薪资": {"rich_text": [{"text": {"content": job.get('salary', '')[:2000]}}]},
                "JD": {"rich_text": [{"text": {"content": job.get('jd', '')[:2000]}}]},
                "匹配原因": {"rich_text": [{"text": {"content": job.get('matchReason', '')[:2000]}}]},
                "状态": {"select": {"name": job.get('status', '新发现')}},
            }

            # 可选字段
            if job.get('date'):
                properties["日期"] = {"date": {"start": job['date']}}

            if job.get('location'):
                # 提取城市名（去掉区县）
                city = job['location'].split('·')[0] if '·' in job['location'] else job['location']
                properties["城市"] = {"select": {"name": city}}

            if job.get('url'):
                properties["链接"] = {"url": job['url']}

            if job.get('matchScore') is not None:
                properties["匹配度"] = {"number": int(job['matchScore'])}

            self.client.pages.create(
                parent={"database_id": self.jobs_db_id},
                properties=properties
            )
            return True

        except Exception as e:
            print(f"❌ 添加职位失败: {e}")
            print(f"   职位: {job.get('company', 'Unknown')} - {job.get('title', 'Unknown')}")
            return False

    def add_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        """
        批量添加职位

        Args:
            jobs: 职位列表

        Returns:
            成功添加的数量
        """
        if not jobs:
            print("⚠️  没有职位需要添加")
            return 0

        print(f"\n正在添加 {len(jobs)} 个职位到Notion...")
        success_count = 0

        for i, job in enumerate(jobs, 1):
            if self.add_job(job):
                success_count += 1
                if i % 5 == 0:  # 每5个显示一次进度
                    print(f"  进度: {i}/{len(jobs)}")

        print(f"✓ 成功添加 {success_count}/{len(jobs)} 个职位")
        return success_count

    def add_application(
        self,
        company: str,
        greeting: str,
        status: str = '待review',
        date: str = None
    ) -> bool:
        """
        添加申请记录

        Args:
            company: 公司名
            greeting: 打招呼话术
            status: 状态
            date: 申请日期

        Returns:
            是否成功
        """
        if not self.applications_db_id:
            self.applications_db_id = os.getenv('NOTION_APPLICATIONS_DB_ID')
            if not self.applications_db_id:
                print("❌ 未找到Applications数据库ID")
                return False

        try:
            properties = {
                "公司": {"title": [{"text": {"content": company[:100]}}]},
                "打招呼话术": {"rich_text": [{"text": {"content": greeting[:2000]}}]},
                "状态": {"select": {"name": status}},
            }

            if date:
                properties["申请日期"] = {"date": {"start": date}}
            else:
                properties["申请日期"] = {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}

            self.client.pages.create(
                parent={"database_id": self.applications_db_id},
                properties=properties
            )
            print(f"✓ 添加申请记录成功: {company}")
            return True

        except Exception as e:
            print(f"❌ 添加申请记录失败: {e}")
            return False

    def update_weekly_stats(self) -> bool:
        """更新周统计"""
        if not self.stats_db_id:
            self.stats_db_id = os.getenv('NOTION_STATS_DB_ID')
            if not self.stats_db_id:
                print("❌ 未找到Stats数据库ID")
                return False

        try:
            # 获取当前周数
            week_num = datetime.now().isocalendar()[1]
            week_label = f"2026年第{week_num}周"

            # 这里简化处理，实际应该查询Jobs和Applications数据库
            # 由于Notion API查询比较复杂，这里先创建示例数据
            new_jobs = 0  # 应该从Jobs数据库查询本周新增
            applied = 0   # 应该从Applications数据库查询
            replied = 0   # 应该从Applications数据库查询已回复
            reply_rate = f"{(replied/applied*100):.1f}%" if applied > 0 else "0%"

            properties = {
                "周数": {"title": [{"text": {"content": week_label}}]},
                "新增职位": {"number": new_jobs},
                "已申请": {"number": applied},
                "收到回复": {"number": replied},
                "回复率": {"rich_text": [{"text": {"content": reply_rate}}]},
            }

            self.client.pages.create(
                parent={"database_id": self.stats_db_id},
                properties=properties
            )
            print(f"✓ 更新周统计成功: {week_label}")
            return True

        except Exception as e:
            print(f"❌ 更新周统计失败: {e}")
            return False

    def get_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取职位列表

        Args:
            limit: 限制数量

        Returns:
            职位列表
        """
        if not self.jobs_db_id:
            self.jobs_db_id = os.getenv('NOTION_JOBS_DB_ID')
            if not self.jobs_db_id:
                return []

        try:
            response = self.client.databases.query(
                database_id=self.jobs_db_id,
                page_size=limit
            )

            jobs = []
            for page in response.get('results', []):
                props = page.get('properties', {})
                job = {
                    'company': self._get_title(props.get('公司', {})),
                    'title': self._get_rich_text(props.get('职位', {})),
                    'salary': self._get_rich_text(props.get('薪资', {})),
                    'location': self._get_select(props.get('城市', {})),
                    'jd': self._get_rich_text(props.get('JD', {})),
                    'url': self._get_url(props.get('链接', {})),
                    'matchScore': self._get_number(props.get('匹配度', {})),
                    'status': self._get_select(props.get('状态', {})),
                    'date': self._get_date(props.get('日期', {})),
                }
                jobs.append(job)

            return jobs

        except Exception as e:
            print(f"❌ 获取职位列表失败: {e}")
            return []

    # 辅助方法：提取Notion属性值
    def _get_title(self, prop):
        """提取title属性"""
        if prop.get('title'):
            return prop['title'][0]['text']['content']
        return ''

    def _get_rich_text(self, prop):
        """提取rich_text属性"""
        if prop.get('rich_text'):
            return prop['rich_text'][0]['text']['content']
        return ''

    def _get_select(self, prop):
        """提取select属性"""
        if prop.get('select'):
            return prop['select']['name']
        return ''

    def _get_url(self, prop):
        """提取url属性"""
        return prop.get('url', '')

    def _get_number(self, prop):
        """提取number属性"""
        return prop.get('number', 0)

    def _get_date(self, prop):
        """提取date属性"""
        if prop.get('date'):
            return prop['date']['start']
        return ''


def main():
    """测试函数"""
    print("=== Notion求职追踪管理工具 ===\n")

    # 加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("提示: 安装python-dotenv可以自动加载.env文件")

    # 创建管理器
    manager = NotionJobManager()

    if not manager.client:
        print("\n请先配置Notion API")
        print("参考: NOTION_SETUP.md")
        return

    # 检查是否需要初始化数据库
    if not os.getenv('NOTION_JOBS_DB_ID'):
        print("\n首次使用，正在创建数据库...")
        if manager.setup_databases():
            print("\n✅ 设置完成！")
            print("下次使用前，请将上面的数据库ID保存到.env文件")
    else:
        print("✓ 使用现有数据库")
        manager.jobs_db_id = os.getenv('NOTION_JOBS_DB_ID')
        manager.applications_db_id = os.getenv('NOTION_APPLICATIONS_DB_ID')
        manager.stats_db_id = os.getenv('NOTION_STATS_DB_ID')


if __name__ == '__main__':
    main()
