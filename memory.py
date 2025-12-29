"""
═══════════════════════════════════════════════════════════════════
  Memory - 轻量级对话记忆管理系统
═══════════════════════════════════════════════════════════════════
  设计哲学：
  - 简洁至上：单一数据结构，无特殊情况
  - 实用主义：只存储真正需要的对话历史
  - 好品味：边界条件自然融入常规逻辑
═══════════════════════════════════════════════════════════════════
"""

from typing import List, Dict
from datetime import datetime


class Memory:
    """对话记忆管理器"""

    def __init__(self, max_size: int = 100):
        """
        初始化记忆系统

        参数：
            max_size: 最大记忆条数，超出后自动清理最旧的记忆
        """
        self.messages: List[Dict] = []
        self.max_size = max_size

    def add(self, role: str, content: str) -> None:
        """
        添加一条记忆

        参数：
            role: 角色 (user/assistant/system)
            content: 消息内容
        """
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # 自动清理：当超过最大容量时，移除最旧的记忆
        if len(self.messages) > self.max_size:
            self.messages.pop(0)

    def get_recent(self, n: int = 10) -> List[Dict]:
        """
        获取最近 n 条记忆

        参数：
            n: 获取的记忆条数

        返回：
            最近的 n 条记忆列表
        """
        return self.messages[-n:]

    def get_all(self) -> List[Dict]:
        """获取所有记忆"""
        return self.messages

    def clear(self) -> None:
        """清空所有记忆"""
        self.messages = []

    def count(self) -> int:
        """获取当前记忆总数"""
        return len(self.messages)

    def format_history(self, n: int = 10) -> str:
        """
        格式化输出对话历史（用于显示）

        参数：
            n: 显示最近 n 条记忆

        返回：
            格式化的对话历史字符串
        """
        recent = self.get_recent(n)
        if not recent:
            return "暂无对话记录"

        lines = []
        for msg in recent:
            role_symbol = "🧑" if msg["role"] == "user" else "🤖"
            lines.append(f"{role_symbol} {msg['role']}: {msg['content']}")

        return "\n".join(lines)
