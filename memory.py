from openai import OpenAI
import chromadb
from typing import List, Dict
import json
from datetime import datetime

class MemorySystem:
    def __init__(self):
        self.client = OpenAI() #对象实例,存储该对象的数据和状态
        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection("episodic")
        self.working_memory = {}  # 当前会话状态
        self.preferences = {}  # 用户偏好(semantic memory)
        
    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    
    def add_episodic(self, content: str, metadata: dict):
        """存储历史对话到向量库"""
        embedding = self.embed(content)
        doc_id = f"ep_{datetime.now().timestamp()}"
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )  #metadata 时间/sessionid。有啥用
    
    def search_episodic(self, query: str, n: int = 3) -> List[Dict]:
        """检索相关历史"""
        query_embedding = self.embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n
        )
        return [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ]
    
    def update_working(self, key: str, value):
        """更新当前会话状态"""
        self.working_memory[key] = value
    
    def get_working(self, key: str):
        """获取会话状态"""
        return self.working_memory.get(key)
    
    def learn_preference(self, key: str, value):
        """学习用户偏好(简化版)"""
        self.preferences[key] = value