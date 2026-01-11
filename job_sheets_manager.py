"""
Google Sheets求职追踪管理工具
用于管理求职信息的Google Sheets表格
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    import pickle
except ImportError:
    print("请先安装Google API库: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    exit(1)


class JobSheetsManager:
    """Google Sheets求职追踪管理器"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, spreadsheet_id: str = None, credentials_path: str = None):
        """
        初始化管理器

        Args:
            spreadsheet_id: Google Sheets的ID（从URL中获取）
            credentials_path: 认证凭据文件路径
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv('SPREADSHEET_ID')
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """认证Google Sheets API"""
        creds = None
        token_path = 'token.pickle'

        # 检查是否已有token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # 如果没有有效凭据，需要登录
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # 检查是否使用服务账号
                if os.path.exists(self.credentials_path):
                    try:
                        creds = service_account.Credentials.from_service_account_file(
                            self.credentials_path, scopes=self.SCOPES
                        )
                        print(f"✓ 使用服务账号认证: {self.credentials_path}")
                    except Exception as e:
                        print(f"服务账号认证失败: {e}")
                        print("请检查credentials.json文件是否正确")
                        print("\n请按照以下步骤获取凭据:")
                        print("1. 访问 https://console.cloud.google.com/")
                        print("2. 创建新项目或选择现有项目")
                        print("3. 启用 Google Sheets API")
                        print("4. 创建服务账号并下载JSON密钥")
                        print("5. 将密钥保存为 credentials.json")
                        print("6. 在Google Sheets中共享文档给服务账号邮箱")
                        return
                else:
                    print(f"未找到凭据文件: {self.credentials_path}")
                    print("请创建凭据文件或设置GOOGLE_CREDENTIALS_PATH环境变量")
                    return

            # 保存token以供下次使用
            if creds and hasattr(creds, 'to_json'):
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)

        try:
            self.service = build('sheets', 'v4', credentials=creds)
            print("✓ Google Sheets API认证成功")
        except HttpError as error:
            print(f"认证失败: {error}")

    def create_job_tracking_sheets(self, spreadsheet_name: str = "AI PM求职追踪"):
        """
        创建包含所有必要sheet的新表格

        Args:
            spreadsheet_name: 表格名称

        Returns:
            spreadsheet_id: 新创建的表格ID
        """
        if not self.service:
            print("未认证，无法创建表格")
            return None

        try:
            spreadsheet = {
                'properties': {'title': spreadsheet_name},
                'sheets': [
                    {
                        'properties': {'title': 'Jobs', 'gridProperties': {'frozenRowCount': 1}},
                    },
                    {
                        'properties': {'title': 'Applications', 'gridProperties': {'frozenRowCount': 1}},
                    },
                    {
                        'properties': {'title': 'WeeklyStats', 'gridProperties': {'frozenRowCount': 1}},
                    }
                ]
            }

            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            self.spreadsheet_id = result['spreadsheetId']

            print(f"✓ 创建表格成功: {spreadsheet_name}")
            print(f"  表格ID: {self.spreadsheet_id}")
            print(f"  URL: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")

            # 初始化表头
            self._init_jobs_headers()
            self._init_applications_headers()
            self._init_weekly_stats_headers()

            return self.spreadsheet_id

        except HttpError as error:
            print(f"创建表格失败: {error}")
            return None

    def _init_jobs_headers(self):
        """初始化Jobs表头"""
        headers = [
            ['日期', '公司', '职位', '薪资', '城市', 'JD', '链接', '匹配度', '匹配原因', '状态']
        ]
        self._write_range('Jobs!A1:J1', headers)
        print("✓ Jobs表头初始化完成")

    def _init_applications_headers(self):
        """初始化Applications表头"""
        headers = [
            ['公司', '申请日期', '打招呼话术', '状态', 'HR回复', '下次联系日期', '备注']
        ]
        self._write_range('Applications!A1:G1', headers)
        print("✓ Applications表头初始化完成")

    def _init_weekly_stats_headers(self):
        """初始化WeeklyStats表头"""
        headers = [
            ['周数', '新增职位', '已申请', '收到回复', '回复率']
        ]
        self._write_range('WeeklyStats!A1:E1', headers)
        print("✓ WeeklyStats表头初始化完成")

    def _write_range(self, range_name: str, values: List[List[Any]]):
        """写入数据到指定范围"""
        if not self.service:
            print("未认证，无法写入数据")
            return False

        try:
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return True
        except HttpError as error:
            print(f"写入数据失败: {error}")
            return False

    def _read_range(self, range_name: str) -> List[List[Any]]:
        """读取指定范围的数据"""
        if not self.service:
            print("未认证，无法读取数据")
            return []

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            print(f"读取数据失败: {error}")
            return []

    def add_jobs(self, jobs: List[Dict[str, Any]]):
        """
        添加职位到Jobs表

        Args:
            jobs: 职位列表，每个职位包含必要字段
        """
        if not jobs:
            print("没有职位数据可添加")
            return

        # 读取现有数据，确定下一行
        existing = self._read_range('Jobs!A:J')
        next_row = len(existing) + 1

        # 准备数据行
        rows = []
        for job in jobs:
            row = [
                job.get('date', datetime.now().strftime('%Y-%m-%d')),
                job.get('company', ''),
                job.get('title', ''),
                job.get('salary', ''),
                job.get('location', ''),
                job.get('jd', '')[:200],  # 限制JD长度
                job.get('url', ''),
                job.get('matchScore', 0),
                job.get('matchReason', ''),
                job.get('status', '新发现')
            ]
            rows.append(row)

        # 写入数据
        range_name = f'Jobs!A{next_row}:J{next_row + len(rows) - 1}'
        if self._write_range(range_name, rows):
            print(f"✓ 成功添加 {len(rows)} 个职位到Jobs表")
        else:
            print("添加职位失败")

    def add_application(self, company: str, greeting: str, status: str = '待review'):
        """
        添加申请记录到Applications表

        Args:
            company: 公司名
            greeting: 打招呼话术
            status: 状态
        """
        existing = self._read_range('Applications!A:G')
        next_row = len(existing) + 1

        row = [
            company,
            datetime.now().strftime('%Y-%m-%d'),
            greeting,
            status,
            '',  # HR回复
            '',  # 下次联系日期
            ''   # 备注
        ]

        range_name = f'Applications!A{next_row}:G{next_row}'
        if self._write_range(range_name, [row]):
            print(f"✓ 成功添加申请记录: {company}")

    def update_weekly_stats(self):
        """更新周统计数据"""
        # 获取当前周数
        week_num = datetime.now().isocalendar()[1]

        # 读取Jobs数据统计
        jobs_data = self._read_range('Jobs!A:J')
        if len(jobs_data) <= 1:  # 只有表头
            print("暂无职位数据，无法更新周统计")
            return

        # 计算本周新增职位
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())

        new_jobs = 0
        applied_jobs = 0

        for row in jobs_data[1:]:  # 跳过表头
            if len(row) < 10:
                continue

            job_date = row[0]
            job_status = row[9]

            try:
                job_datetime = datetime.strptime(job_date, '%Y-%m-%d')
                if job_datetime >= week_start:
                    new_jobs += 1
                    if job_status in ['已申请', '待申请']:
                        applied_jobs += 1
            except:
                pass

        # 读取Applications数据
        apps_data = self._read_range('Applications!A:G')
        replied = sum(1 for row in apps_data[1:] if len(row) >= 4 and row[3] == '已回复')

        reply_rate = f"{(replied/applied_jobs*100):.1f}%" if applied_jobs > 0 else "0%"

        # 更新WeeklyStats
        stats_data = self._read_range('WeeklyStats!A:E')
        next_row = len(stats_data) + 1

        row = [f"第{week_num}周", new_jobs, applied_jobs, replied, reply_rate]
        range_name = f'WeeklyStats!A{next_row}:E{next_row}'

        if self._write_range(range_name, [row]):
            print(f"✓ 更新第{week_num}周统计: 新增{new_jobs}个职位, 已申请{applied_jobs}个")

    def get_jobs(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取Jobs表中的职位列表

        Args:
            limit: 限制返回数量

        Returns:
            职位列表
        """
        data = self._read_range('Jobs!A:J')
        if len(data) <= 1:
            return []

        headers = data[0]
        jobs = []

        for row in data[1:limit+1 if limit else None]:
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))

            job = {
                'date': row[0],
                'company': row[1],
                'title': row[2],
                'salary': row[3],
                'location': row[4],
                'jd': row[5],
                'url': row[6],
                'matchScore': row[7],
                'matchReason': row[8],
                'status': row[9]
            }
            jobs.append(job)

        return jobs


def main():
    """主函数 - 用于测试"""
    print("=== Google Sheets求职追踪管理工具 ===\n")

    # 创建管理器实例
    manager = JobSheetsManager()

    if not manager.service:
        print("\n请先配置Google Sheets API认证")
        return

    # 创建新表格（如果需要）
    if not manager.spreadsheet_id:
        print("\n正在创建新的求职追踪表格...")
        spreadsheet_id = manager.create_job_tracking_sheets()
        if spreadsheet_id:
            print(f"\n请将以下ID保存到环境变量SPREADSHEET_ID中:")
            print(f"export SPREADSHEET_ID='{spreadsheet_id}'")
    else:
        print(f"\n使用现有表格: {manager.spreadsheet_id}")
        print(f"URL: https://docs.google.com/spreadsheets/d/{manager.spreadsheet_id}")


if __name__ == '__main__':
    from datetime import timedelta
    main()
