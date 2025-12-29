from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from agent import MemoryAgent
import threading

app = Flask(__name__)
CORS(app)

# 初始化 agent (线程安全)
agent = MemoryAgent()
agent_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')

        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        # 使用锁保证线程安全
        with agent_lock:
            response = agent.chat(user_message, user_id)

        return jsonify({
            'response': response,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memories', methods=['GET'])
def get_memories():
    """获取相关记忆"""
    try:
        query = request.args.get('query', '')
        n = int(request.args.get('n', 5))

        with agent_lock:
            memories = agent.memory.search_episodic(query, n=n)

        return jsonify({
            'memories': memories,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 启动服务器在 http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
