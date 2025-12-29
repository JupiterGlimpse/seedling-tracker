"""
═══════════════════════════════════════════════════════════════════
  Agent - 智能对话代理
═══════════════════════════════════════════════════════════════════
  设计哲学：
  - 简洁执念：核心逻辑清晰，无冗余分支
  - 实用主义：解决真实对话需求，可扩展到真实 LLM
  - 可测试性：纯函数设计，易于测试和调试
═══════════════════════════════════════════════════════════════════
"""

from memory import Memory
import random
from typing import Optional


class Agent:
    """对话代理核心"""

    def __init__(self, name: str = "Seedling Bot", memory_size: int = 100):
        """
        初始化代理

        参数：
            name: 代理名称
            memory_size: 记忆容量
        """
        self.name = name
        self.memory = Memory(max_size=memory_size)
        self.context = ""  # 当前会话上下文

    def chat(self, user_input: str) -> str:
        """
        处理用户输入并生成回复

        参数：
            user_input: 用户输入的消息

        返回：
            代理的回复
        """
        # 存储用户消息
        self.memory.add("user", user_input)

        # 生成回复
        response = self._generate_response(user_input)

        # 存储代理回复
        self.memory.add("assistant", response)

        return response

    def _generate_response(self, user_input: str) -> str:
        """
        生成回复内容（核心逻辑）

        参数：
            user_input: 用户输入

        返回：
            生成的回复
        """
        # 命令处理
        cmd_response = self._handle_command(user_input)
        if cmd_response:
            return cmd_response

        # 简单的模式匹配回复（可替换为真实 LLM 调用）
        return self._pattern_match(user_input)

    def _handle_command(self, text: str) -> Optional[str]:
        """
        处理特殊命令

        参数：
            text: 用户输入

        返回：
            命令执行结果，如果不是命令则返回 None
        """
        commands = {
            "/help": self._help,
            "/clear": self._clear_memory,
            "/history": self._show_history,
            "/stats": self._show_stats,
        }

        cmd = text.strip().lower()
        handler = commands.get(cmd)

        return handler() if handler else None

    def _pattern_match(self, text: str) -> str:
        """
        基于模式匹配生成回复

        参数：
            text: 用户输入

        返回：
            匹配到的回复
        """
        text_lower = text.lower()

        # ─────────────────────────────────────
        # 问候类
        # ─────────────────────────────────────
        if any(word in text_lower for word in ["你好", "hi", "hello"]):
            return random.choice([
                f"你好！我是 {self.name}，有什么可以帮你的？",
                "嗨！很高兴见到你！",
                "你好呀！今天想聊点什么？"
            ])

        # ─────────────────────────────────────
        # 询问类
        # ─────────────────────────────────────
        if any(word in text_lower for word in ["是谁", "你是", "介绍"]):
            return f"我是 {self.name}，一个简单的对话代理。我可以记住我们的对话历史，并尝试理解你的需求。"

        if any(word in text_lower for word in ["能做", "功能", "会什么"]):
            return "我可以：\n• 记住对话历史\n• 回答简单问题\n• 执行命令（输入 /help 查看）"

        # ─────────────────────────────────────
        # 情感类
        # ─────────────────────────────────────
        if any(word in text_lower for word in ["谢谢", "感谢", "thank"]):
            return random.choice(["不客气！", "很高兴能帮到你！", "随时为你服务！"])

        if any(word in text_lower for word in ["再见", "拜拜", "bye"]):
            return random.choice(["再见！", "下次再聊！", "期待下次见面！"])

        # ─────────────────────────────────────
        # 默认回复
        # ─────────────────────────────────────
        return random.choice([
            f"我听到你说：「{text}」。这很有趣！",
            "嗯，继续说说看。",
            "我在思考你说的话...",
            "有意思！能详细说说吗？",
            f"关于「{text}」，我会记在心里的。"
        ])

    # ═════════════════════════════════════════════════════════════
    # 命令处理器
    # ═════════════════════════════════════════════════════════════

    def _help(self) -> str:
        """显示帮助信息"""
        return """
可用命令：
  /help     - 显示此帮助信息
  /clear    - 清空对话记忆
  /history  - 查看对话历史
  /stats    - 查看统计信息
        """.strip()

    def _clear_memory(self) -> str:
        """清空记忆"""
        count = self.memory.count()
        self.memory.clear()
        return f"✅ 已清空 {count} 条对话记录"

    def _show_history(self) -> str:
        """显示对话历史"""
        return self.memory.format_history(20)

    def _show_stats(self) -> str:
        """显示统计信息"""
        total = self.memory.count()
        user_msgs = sum(1 for m in self.memory.get_all() if m["role"] == "user")
        bot_msgs = sum(1 for m in self.memory.get_all() if m["role"] == "assistant")

        return f"""
📊 统计信息
━━━━━━━━━━━━━━━━━━━━
总消息数：{total}
用户消息：{user_msgs}
代理回复：{bot_msgs}
记忆容量：{self.memory.max_size}
        """.strip()

    def reset(self) -> None:
        """重置代理状态"""
        self.memory.clear()
        self.context = ""
