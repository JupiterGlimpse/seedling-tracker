"""
═══════════════════════════════════════════════════════════════════
  Seedling Tracker - Web 前端界面
═══════════════════════════════════════════════════════════════════
  技术选型：Gradio
  - 零配置：一行代码启动 Web 服务
  - 高性能：自动处理并发和状态管理
  - 美观：Material Design 风格界面
═══════════════════════════════════════════════════════════════════
"""

import gradio as gr
from agent import Agent


# ═════════════════════════════════════════════════════════════
# 全局状态
# ═════════════════════════════════════════════════════════════

agent = Agent(name="Seedling Bot")


# ═════════════════════════════════════════════════════════════
# 核心逻辑
# ═════════════════════════════════════════════════════════════

def chat_response(message: str, history: list) -> str:
    """
    处理用户消息并返回回复

    参数：
        message: 用户输入的消息
        history: 对话历史（Gradio 自动管理）

    返回：
        代理的回复
    """
    if not message.strip():
        return "请输入有效的消息"

    return agent.chat(message)


def clear_history():
    """
    清空对话历史

    返回：
        清空后的提示信息和空历史
    """
    agent.reset()
    return None, "历史记录已清空"


def show_stats() -> str:
    """
    显示统计信息

    返回：
        统计信息字符串
    """
    return agent._show_stats()


# ═════════════════════════════════════════════════════════════
# 界面构建
# ═════════════════════════════════════════════════════════════

def create_interface():
    """构建 Gradio 界面"""

    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="Seedling Tracker"
    ) as demo:

        gr.Markdown("""
        # 🌱 Seedling Tracker
        一个简单优雅的对话代理系统，具备记忆功能
        """)

        with gr.Row():
            with gr.Column(scale=4):
                # 聊天界面
                chatbot = gr.Chatbot(
                    label="对话窗口",
                    height=500,
                    show_label=True,
                    avatar_images=(None, "🤖")
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="输入消息",
                        placeholder="输入你的消息... (支持命令: /help, /clear, /history, /stats)",
                        lines=2,
                        scale=4
                    )
                    submit = gr.Button("发送", variant="primary", scale=1)

                with gr.Row():
                    clear = gr.Button("🗑️ 清空历史", variant="secondary")

            with gr.Column(scale=1):
                # 侧边栏：统计信息
                gr.Markdown("### 📊 系统信息")
                stats_display = gr.Textbox(
                    label="统计",
                    lines=8,
                    interactive=False
                )
                refresh_stats = gr.Button("刷新统计")

        gr.Markdown("""
        ---
        ### 💡 使用提示
        - 输入 `/help` 查看可用命令
        - 输入 `/history` 查看对话历史
        - 输入 `/stats` 查看详细统计
        - 输入 `/clear` 清空记忆
        """)

        # ─────────────────────────────────────
        # 事件绑定
        # ─────────────────────────────────────

        # 发送消息
        msg.submit(
            fn=chat_response,
            inputs=[msg, chatbot],
            outputs=[chatbot],
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )

        submit.click(
            fn=chat_response,
            inputs=[msg, chatbot],
            outputs=[chatbot],
        ).then(
            fn=lambda: "",
            outputs=[msg]
        )

        # 清空历史
        clear.click(
            fn=clear_history,
            outputs=[chatbot, stats_display]
        )

        # 刷新统计
        refresh_stats.click(
            fn=show_stats,
            outputs=[stats_display]
        )

        # 页面加载时显示统计
        demo.load(
            fn=show_stats,
            outputs=[stats_display]
        )

    return demo


# ═════════════════════════════════════════════════════════════
# 启动服务
# ═════════════════════════════════════════════════════════════

if __name__ == "__main__":
    demo = create_interface()

    print("🌱 Seedling Tracker 启动中...")
    print("━" * 50)

    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,
        share=False,            # 本地测试不需要公网链接
        show_api=False          # 隐藏 API 文档
    )
