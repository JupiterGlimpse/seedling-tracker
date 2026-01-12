"""
Boss直聘职位爬虫（Python版本）
用于搜索和提取Boss直聘上的职位信息
"""

import json
import time
from typing import List, Dict, Any
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    print(f"请安装依赖: {e}")
    print("pip install selenium webdriver-manager")
    exit(1)


class BossJobScraper:
    """Boss直聘职位爬虫"""

    # 城市代码映射
    CITY_CODES = {
        '北京': '101010100',
        '上海': '101020100',
        '广州': '101280100',
        '深圳': '101280600',
        '杭州': '101210100',
        '成都': '101270100',
        '南京': '101190100',
        '武汉': '101200100',
        '西安': '101110100',
    }

    # 经验要求代码
    EXPERIENCE_CODES = {
        '应届生': '101',
        '1年以内': '102',
        '1-3年': '103',
        '3-5年': '104',
        '5-10年': '105',
        '10年以上': '106',
    }

    def __init__(self, headless: bool = True):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """初始化Selenium WebDriver（自动管理ChromeDriver）"""
        if self.driver:
            return

        options = Options()
        if self.headless:
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            # 使用webdriver-manager自动下载和管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✓ Chrome WebDriver初始化成功（自动管理）")
        except Exception as e:
            print(f"❌ 初始化WebDriver失败: {e}")
            print("\n请确保已安装Chrome浏览器")
            print("macOS: 从 https://www.google.com/chrome/ 下载")
            print("Ubuntu: sudo apt-get install google-chrome-stable")
            raise

    def search_jobs(
        self,
        keyword: str,
        city: str = '北京',
        experience: str = None,
        page: int = 1,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索职位

        Args:
            keyword: 搜索关键词（如"AI产品经理"）
            city: 城市名称或城市代码
            experience: 工作经验要求
            page: 页码
            max_results: 最大结果数

        Returns:
            职位列表
        """
        self._init_driver()

        # 获取城市代码
        city_code = self.CITY_CODES.get(city, city)

        # 构建URL
        url = f'https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}&page={page}'

        if experience and experience in self.EXPERIENCE_CODES:
            url += f'&experience={self.EXPERIENCE_CODES[experience]}'

        print(f"正在访问: {url}")

        try:
            self.driver.get(url)

            # 等待页面加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'job-card-wrapper'))
                )
            except TimeoutException:
                print("警告: 页面加载超时，可能需要登录或遇到反爬虫")
                # 检查是否需要登录
                if "login" in self.driver.current_url:
                    print("检测到需要登录，请手动登录后重试")
                    time.sleep(30)  # 给用户时间登录
                return []

            # 等待一下让页面完全加载
            time.sleep(2)

            # 提取职位信息
            jobs = []
            job_cards = self.driver.find_elements(By.CLASS_NAME, 'job-card-wrapper')

            print(f"找到 {len(job_cards)} 个职位卡片")

            for card in job_cards[:max_results]:
                try:
                    job = self._extract_job_info(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    print(f"提取职位信息出错: {e}")
                    continue

            return jobs

        except Exception as e:
            print(f"搜索职位失败: {e}")
            return []

    def _extract_job_info(self, card_element) -> Dict[str, Any]:
        """从职位卡片提取信息"""
        try:
            # 基本信息
            job_name = card_element.find_element(By.CLASS_NAME, 'job-name').text.strip()
            salary = card_element.find_element(By.CLASS_NAME, 'salary').text.strip()

            # 公司信息
            company_name = card_element.find_element(By.CLASS_NAME, 'company-name').text.strip()

            # 地点
            try:
                job_area = card_element.find_element(By.CLASS_NAME, 'job-area').text.strip()
            except NoSuchElementException:
                job_area = ''

            # 标签
            try:
                tag_elements = card_element.find_elements(By.CSS_SELECTOR, '.tag-list li')
                tags = ' / '.join([tag.text.strip() for tag in tag_elements])
            except:
                tags = ''

            # 公司标签
            try:
                company_tag_elements = card_element.find_elements(By.CSS_SELECTOR, '.company-tag-list li')
                company_info = ' / '.join([tag.text.strip() for tag in company_tag_elements])
            except:
                company_info = ''

            # JD简介
            try:
                info_desc = card_element.find_element(By.CLASS_NAME, 'info-desc').text.strip()
            except:
                info_desc = ''

            # 职位链接
            try:
                link_element = card_element.find_element(By.CSS_SELECTOR, 'a.job-card-left')
                job_url = link_element.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = 'https://www.zhipin.com' + job_url
            except:
                job_url = ''

            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'company': company_name,
                'companyInfo': company_info,
                'title': job_name,
                'salary': salary,
                'location': job_area,
                'tags': tags,
                'jd': info_desc[:200],  # 限制长度
                'url': job_url,
                'matchScore': 0,
                'matchReason': '',
                'status': '新发现'
            }

        except Exception as e:
            print(f"提取单个职位信息失败: {e}")
            return None

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✓ 浏览器已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """测试函数"""
    print("=== Boss直聘职位爬虫测试 ===\n")

    # 创建爬虫实例
    with BossJobScraper(headless=False) as scraper:
        # 搜索职位
        jobs = scraper.search_jobs(
            keyword='AI产品经理',
            city='北京',
            page=1,
            max_results=5
        )

        # 输出结果
        print(f"\n找到 {len(jobs)} 个职位:\n")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['company']} - {job['title']}")
            print(f"   薪资: {job['salary']}")
            print(f"   地点: {job['location']}")
            print(f"   链接: {job['url']}")
            print()

        # 保存到JSON文件
        if jobs:
            output_file = 'jobs_output.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            print(f"✓ 结果已保存到 {output_file}")


if __name__ == '__main__':
    main()
