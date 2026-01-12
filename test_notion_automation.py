#!/usr/bin/env python3
"""
求职自动化系统测试脚本（Notion版本）
整合Boss直聘爬虫和Notion管理
"""

import os
import sys
import json
from datetime import datetime

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ 加载.env文件成功")
except ImportError:
    print("提示: 安装python-dotenv可自动加载.env文件")
    print("pip install python-dotenv")

# 导入自定义模块
try:
    from boss_scraper import BossJobScraper
    from notion_manager import NotionJobManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保boss_scraper.py和notion_manager.py在同一目录下")
    sys.exit(1)


def print_job(job: dict, index: int = None):
    """格式化打印职位信息"""
    if index:
        print(f"\n{'='*60}")
        print(f"职位 #{index}")
        print('='*60)

    print(f"📅 日期: {job.get('date', 'N/A')}")
    print(f"🏢 公司: {job.get('company', 'N/A')}")
    if job.get('companyInfo'):
        print(f"   公司信息: {job.get('companyInfo', 'N/A')}")
    print(f"💼 职位: {job.get('title', 'N/A')}")
    print(f"💰 薪资: {job.get('salary', 'N/A')}")
    print(f"📍 地点: {job.get('location', 'N/A')}")
    if job.get('tags'):
        print(f"🏷️  标签: {job.get('tags', 'N/A')}")
    print(f"📝 描述: {job.get('jd', 'N/A')[:100]}...")
    print(f"🔗 链接: {job.get('url', 'N/A')}")
    print(f"📊 匹配度: {job.get('matchScore', 0)}")
    print(f"📌 状态: {job.get('status', 'N/A')}")


def test_boss_scraper():
    """测试Boss直聘爬虫"""
    print("\n" + "="*70)
    print("测试 1: Boss直聘职位爬虫")
    print("="*70)

    try:
        with BossJobScraper(headless=True) as scraper:
            print("\n正在搜索: AI产品经理 - 北京...")

            jobs = scraper.search_jobs(
                keyword='AI产品经理',
                city='北京',
                page=1,
                max_results=5
            )

            if not jobs:
                print("❌ 未找到职位，可能需要登录或遇到反爬虫")
                print("建议:")
                print("1. 尝试使用headless=False手动登录")
                print("2. 检查网络连接")
                print("3. 使用MCP Server方式（需要配置）")
                return []

            print(f"\n✓ 成功获取 {len(jobs)} 个职位")

            # 显示前5个职位
            print("\n【前5个职位详情】")
            for i, job in enumerate(jobs[:5], 1):
                print_job(job, i)

            # 保存到JSON
            output_file = 'test_jobs.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 职位数据已保存到: {output_file}")

            return jobs

    except Exception as e:
        print(f"\n❌ 爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_notion(jobs: list = None):
    """测试Notion集成"""
    print("\n" + "="*70)
    print("测试 2: Notion集成")
    print("="*70)

    # 检查环境变量
    api_key = os.getenv('NOTION_API_KEY')
    page_id = os.getenv('NOTION_PAGE_ID')

    if not api_key:
        print("\n⚠️  未找到NOTION_API_KEY")
        print("\n请按以下步骤配置（超简单，只需5分钟！）:")
        print("\n📝 步骤1: 创建Integration")
        print("   1. 访问 https://www.notion.so/my-integrations")
        print("   2. 点击 '+ New integration'")
        print("   3. 填写名称（如：Job Tracker Bot）")
        print("   4. 复制 Integration Token")
        print("\n📝 步骤2: 配置环境变量")
        print("   创建.env文件并添加:")
        print("   NOTION_API_KEY=secret_你的Token")
        print("   NOTION_PAGE_ID=你的PageID")
        print("\n📝 步骤3: 在Notion中连接")
        print("   1. 创建新页面")
        print("   2. 点击右上角 '...' → 'Add connections'")
        print("   3. 选择你的Integration")
        print("\n📚 详细教程: NOTION_SETUP.md")
        return

    if not page_id:
        print("\n⚠️  未找到NOTION_PAGE_ID")
        print("\n快速获取:")
        print("1. 在Notion中打开页面")
        print("2. URL中的32位字符就是Page ID")
        print("   https://notion.so/xxxxx-<这32位>?xxx")
        print("\n3. 添加到.env文件:")
        print("   NOTION_PAGE_ID=你的32位ID")
        return

    try:
        manager = NotionJobManager(api_key=api_key, page_id=page_id)

        if not manager.client:
            print("\n❌ Notion API连接失败")
            return

        # 检查是否需要初始化数据库
        jobs_db_id = os.getenv('NOTION_JOBS_DB_ID')

        if not jobs_db_id:
            print("\n首次使用，正在创建Notion数据库...")
            if manager.setup_databases():
                print("\n✅ 数据库创建成功！")
                print("\n⚠️  重要：请将上面输出的数据库ID保存到.env文件")
                print("这样下次就不需要重新创建了")
            else:
                print("\n❌ 数据库创建失败")
                return
        else:
            print(f"\n✓ 使用现有数据库")
            manager.jobs_db_id = jobs_db_id
            manager.applications_db_id = os.getenv('NOTION_APPLICATIONS_DB_ID')
            manager.stats_db_id = os.getenv('NOTION_STATS_DB_ID')

        # 如果有职位数据，添加到Notion
        if jobs and manager.jobs_db_id:
            print(f"\n正在添加 {len(jobs)} 个职位到Notion...")
            success_count = manager.add_jobs(jobs)

            if success_count > 0:
                print(f"\n✓ 成功添加 {success_count} 个职位！")
                print(f"\n📱 在Notion中查看:")
                print(f"   https://notion.so/{page_id}")

                # 读取并显示前5条
                print("\n【Notion中的前5个职位】")
                saved_jobs = manager.get_jobs(limit=5)
                for i, job in enumerate(saved_jobs, 1):
                    print_job(job, i)
            else:
                print("\n⚠️  未能添加职位，请检查数据库配置")

        print("\n✓ Notion测试完成")

    except Exception as e:
        print(f"\n❌ Notion测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试流程"""
    print("\n" + "🚀"*35)
    print("AI PM 求职自动化系统测试（Notion版本）")
    print("🚀"*35)

    print("\n⚙️  环境检查:")
    print(f"  Python版本: {sys.version}")
    print(f"  工作目录: {os.getcwd()}")

    # 检查依赖
    try:
        import selenium
        print(f"  ✓ Selenium: {selenium.__version__}")
    except ImportError:
        print("  ❌ Selenium未安装 (pip install selenium)")

    try:
        import notion_client
        print(f"  ✓ Notion Client: 已安装")
    except ImportError:
        print("  ❌ Notion Client未安装")
        print("     pip install notion-client python-dotenv")

    # 检查环境变量
    print("\n⚙️  配置检查:")
    if os.getenv('NOTION_API_KEY'):
        print("  ✓ NOTION_API_KEY: 已设置")
    else:
        print("  ❌ NOTION_API_KEY: 未设置（请查看NOTION_SETUP.md）")

    if os.getenv('NOTION_PAGE_ID'):
        print("  ✓ NOTION_PAGE_ID: 已设置")
    else:
        print("  ❌ NOTION_PAGE_ID: 未设置（请查看NOTION_SETUP.md）")

    # 测试1: Boss直聘爬虫
    jobs = test_boss_scraper()

    # 测试2: Notion集成
    test_notion(jobs)

    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)

    print("\n📝 下一步:")
    print("1. 配置Notion API（如果还未配置）- 参考 NOTION_SETUP.md")
    print("2. 保存数据库ID到.env文件（如果是首次运行）")
    print("3. 运行完整的求职自动化流程: python3 daily_job_search_notion.py")
    print("4. (可选) 配置MCP Server用于Claude Desktop/Cursor集成")

    print("\n💡 提示:")
    print("  Notion配置比Google Sheets简单得多，只需要:")
    print("  - 一个API Key（2分钟获取）")
    print("  - 一个Page ID（复制URL即可）")
    print("  无需下载凭据文件，无需设置服务账号！")


if __name__ == '__main__':
    main()
