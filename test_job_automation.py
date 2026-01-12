#!/usr/bin/env python3
"""
求职自动化系统测试脚本
整合Boss直聘爬虫和Google Sheets管理
"""

import os
import sys
import json
from datetime import datetime

# 导入自定义模块
try:
    from boss_scraper import BossJobScraper
    from job_sheets_manager import JobSheetsManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保boss_scraper.py和job_sheets_manager.py在同一目录下")
    sys.exit(1)


def print_job(job: dict, index: int = None):
    """格式化打印职位信息"""
    if index:
        print(f"\n{'='*60}")
        print(f"职位 #{index}")
        print('='*60)

    print(f"📅 日期: {job.get('date', 'N/A')}")
    print(f"🏢 公司: {job.get('company', 'N/A')}")
    print(f"   公司信息: {job.get('companyInfo', 'N/A')}")
    print(f"💼 职位: {job.get('title', 'N/A')}")
    print(f"💰 薪资: {job.get('salary', 'N/A')}")
    print(f"📍 地点: {job.get('location', 'N/A')}")
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


def test_google_sheets(jobs: list = None):
    """测试Google Sheets集成"""
    print("\n" + "="*70)
    print("测试 2: Google Sheets集成")
    print("="*70)

    # 检查环境变量
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

    if not os.path.exists(credentials_path):
        print(f"\n⚠️  未找到Google API凭据文件: {credentials_path}")
        print("\n请按以下步骤配置:")
        print("1. 访问 https://console.cloud.google.com/")
        print("2. 创建新项目或选择现有项目")
        print("3. 启用 Google Sheets API")
        print("4. 创建服务账号凭据")
        print("5. 下载JSON密钥文件并保存为 credentials.json")
        print("6. 设置环境变量:")
        print("   export GOOGLE_CREDENTIALS_PATH='credentials.json'")
        return

    try:
        manager = JobSheetsManager(
            spreadsheet_id=spreadsheet_id,
            credentials_path=credentials_path
        )

        if not manager.service:
            print("\n❌ Google Sheets API认证失败")
            return

        # 如果没有spreadsheet_id，创建新表格
        if not manager.spreadsheet_id:
            print("\n正在创建新的求职追踪表格...")
            new_id = manager.create_job_tracking_sheets("AI PM求职追踪")

            if new_id:
                print(f"\n✓ 表格创建成功!")
                print(f"  表格ID: {new_id}")
                print(f"  URL: https://docs.google.com/spreadsheets/d/{new_id}")
                print(f"\n请保存表格ID到环境变量:")
                print(f"  export SPREADSHEET_ID='{new_id}'")
                print(f"\n⚠️  重要: 请在Google Sheets中将表格共享给服务账号邮箱")
                print(f"  (邮箱地址在credentials.json的client_email字段)")
        else:
            print(f"\n✓ 使用现有表格: {manager.spreadsheet_id}")

        # 如果有职位数据，添加到表格
        if jobs:
            print(f"\n正在添加 {len(jobs)} 个职位到Google Sheets...")
            manager.add_jobs(jobs)

            # 读取并显示前5条
            print("\n【Google Sheets中的前5个职位】")
            saved_jobs = manager.get_jobs(limit=5)
            for i, job in enumerate(saved_jobs, 1):
                print_job(job, i)

        print("\n✓ Google Sheets测试完成")

    except Exception as e:
        print(f"\n❌ Google Sheets测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试流程"""
    print("\n" + "🚀"*35)
    print("AI PM 求职自动化系统测试")
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
        import google.auth
        print("  ✓ Google API库已安装")
    except ImportError:
        print("  ❌ Google API库未安装")
        print("     pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

    # 测试1: Boss直聘爬虫
    jobs = test_boss_scraper()

    # 测试2: Google Sheets集成
    test_google_sheets(jobs)

    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)

    print("\n📝 下一步:")
    print("1. 配置Google Sheets API凭据（如果还未配置）")
    print("2. 设置SPREADSHEET_ID环境变量")
    print("3. 运行完整的求职自动化流程")
    print("4. (可选) 配置MCP Server用于Claude Desktop/Cursor集成")


if __name__ == '__main__':
    main()
