'''欢迎来到大模型开发框架实战课

作者 杨勇'''

# 1.这里加载 key
from config.load_key import load_key
import os
load_key()
from fontTools.ttLib.tables.ttProgram import instructions

# 2.加载向量库和索引
persist_path = './knowledge_base/test'
if not os.path.exists(persist_path):
    raise FileNotFoundError(f"知识库路径 {persist_path} 不存在，请检查配置")

from chatbot import rag
index = rag.load_index(persist_path=persist_path)
query_engine = rag.create_query_engine(index=index)

# 添加调试日志
print(f"索引加载成功，路径：{persist_path}")


# 3. 问答系统的UI实现采用 flask框架
from flask import Flask, request, jsonify, Response, render_template
import json

app = Flask(__name__)  # Flask APP

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 接收用户输入作为问题
        question = request.form.get('question')
        
        # 流式输出：使用 Response 包裹生成器
        def generate():
            try:
                # 调用流式 ask 函数（返回生成器）
                for chunk in rag.ask_stream(question, query_engine=query_engine):
                    # 返回纯文本流（适合逐步显示生成内容）
                    print(f"生成内容: {chunk}")  # ✅ 添加日志，确认是否有内容
                    yield chunk
                    
            except Exception as e:
                print(f"错误: {str(e)}")
                yield f"【系统错误】{str(e)}"

        # 生成器封装为 Flask 流式响应，返回流式响应（mimetype="text/plain" 表示纯文本流）适合逐步显示大模型生成内容
        return Response(generate(), mimetype="text/plain")

    return render_template('index_opt.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False, port=5000)