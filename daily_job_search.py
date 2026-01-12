#!/usr/bin/env python3
"""
每日求职自动化脚本
自动搜索职位并保存到Google Sheets
"""

import os
import sys
from datetime import datetime

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("提示: 安装python-dotenv可以自动加载.env文件")
    print("pip install python-dotenv")

# 导入自定义模块
try:
    from boss_scraper import BossJobScraper
    from job_sheets_manager import JobSheetsManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)


def print_banner():
    """打印banner"""
    print("\n" + "="*70)
    print("🚀 AI PM 每日求职自动化")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def search_and_save_jobs(
    keyword: str = 'AI产品经理',
    city: str = '北京',
    max_results: int = 20
):
    """
    搜索职位并保存到Google Sheets

    Args:
        keyword: 搜索关键词
        city: 城市
        max_results: 最大结果数
    """
    print(f"🔍 搜索条件: {keyword} - {city}")
    print(f"   最大结果数: {max_results}\n")

    # 1. 搜索职位
    print("正在抓取Boss直聘职位...")
    try:
        with BossJobScraper(headless=True) as scraper:
            jobs = scraper.search_jobs(
                keyword=keyword,
                city=city,
                page=1,
                max_results=max_results
            )
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 尝试使用headless=False手动登录")
        print("3. 检查ChromeDriver是否正确安装")
        return

    if not jobs:
        print("⚠️  未找到职位")
        print("   可能原因:")
        print("   - 需要登录Boss直聘")
        print("   - 搜索条件过于严格")
        print("   - 遇到反爬虫限制")
        return

    print(f"✓ 成功获取 {len(jobs)} 个职位\n")

    # 2. 显示前5个职位预览
    print("【前5个职位预览】")
    print("-" * 70)
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. {job['company']} - {job['title']}")
        print(f"   💰 {job['salary']} | 📍 {job['location']}")
        print(f"   🔗 {job['url'][:60]}...")
        print()

    # 3. 保存到Google Sheets
    print("💾 正在保存到Google Sheets...")
    try:
        manager = JobSheetsManager()

        if not manager.service:
            print("❌ Google Sheets认证失败")
            print("   请检查credentials.json配置")
            return

        if not manager.spreadsheet_id:
            print("⚠️  未设置SPREADSHEET_ID环境变量")
            print("   正在创建新表格...")
            spreadsheet_id = manager.create_job_tracking_sheets()
            if spreadsheet_id:
                print(f"\n✓ 新表格创建成功: {spreadsheet_id}")
                print(f"   请保存此ID到.env文件:")
                print(f"   SPREADSHEET_ID={spreadsheet_id}")
            else:
                print("❌ 创建表格失败")
                return

        # 添加职位
        manager.add_jobs(jobs)

        # 更新周统计
        print("📊 正在更新周统计...")
        manager.update_weekly_stats()

        print("\n✅ 数据保存成功!")
        print(f"   查看表格: https://docs.google.com/spreadsheets/d/{manager.spreadsheet_id}")

    except Exception as e:
        print(f"❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()

    # 4. 生成总结
    print("\n" + "="*70)
    print("📈 今日总结")
    print("="*70)
    print(f"新增职位: {len(jobs)}")
    print(f"搜索关键词: {keyword}")
    print(f"目标城市: {city}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 建议:")
    print("   1. 登录Google Sheets查看完整职位列表")
    print("   2. 手动标记感兴趣的职位匹配度")
    print("   3. 在Applications表中记录申请进度")
    print("="*70 + "\n")


def main():
    """主函数"""
    print_banner()

    # 从环境变量或命令行参数获取配置
    keyword = os.getenv('JOB_KEYWORD', 'AI产品经理')
    city = os.getenv('JOB_CITY', '北京')
    max_results = int(os.getenv('JOB_MAX_RESULTS', '20'))

    # 支持命令行参数覆盖
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    if len(sys.argv) > 2:
        city = sys.argv[2]
    if len(sys.argv) > 3:
        max_results = int(sys.argv[3])

    search_and_save_jobs(keyword, city, max_results)


if __name__ == '__main__':
    main()
