from openai import OpenAI
from memory import MemorySystem
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()


class MemoryAgent:
    def __init__(self):
        self.client = OpenAI()
        self.memory = MemorySystem()


    def import_history(self, json_file: str):
        """导入历史对话到memory。格式解析"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 假设格式: [{"user": "...", "assistant": "...", "timestamp": "..."}]
        for item in data:
            conversation = f"User: {item['user']}\nAssistant: {item['assistant']}"
            self.memory.add_episodic(
                conversation,
                {"timestamp": item.get('timestamp', 'unknown')}
            )
        print(f"导入 {len(data)} 条对话") 


    def chat(self, user_message: str, user_id: str = "default") -> str:
        # 1. 检索相关历史
        relevant_memories = self.memory.search_episodic(user_message, n=3)
        context = "\n".join([m['content'] for m in relevant_memories])
        
        # 2. 构建prompt
        system_prompt = f"""你是任务执行助手。
        
            相关历史记录:
            {context if context else '(无历史)'}

            基于历史提供个性化建议。"""
                    
        # 3. 调用LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        assistant_message = response.choices[0].message.content
        
        # 4. 存储到memory
        conversation = f"User: {user_message}\nAssistant: {assistant_message}"
        self.memory.add_episodic(
            conversation,
            {"user_id": user_id, "timestamp": str(datetime.now())}
        )
        
        return assistant_message

# 使用
if __name__ == "__main__":
    agent = MemoryAgent()
    
    print("Chat (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            break
        
        response = agent.chat(user_input)
        print(f"AI: {response}\n")