'''欢迎来到联通大模型开发框架实战课

作者 杨勇'''

# 这里写昨天的agengt类似的代码
from fontTools.ttLib.tables.ttProgram import instructions

from chatbot import rag
index = rag.load_index()
query_engine = rag.create_query_engine(index=index)

# 5. Output 问答系统的UI实现
from flask import Flask, request, jsonify, render_template
app = Flask(__name__) # Flask APP

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        # 接收用户输入作为问题
        question = request.form.get('question')        
        
        # RetrievalQA链 - 读入问题，生成答案
        result = rag.ask(question, query_engine=query_engine)
        source_documents = result["source_documents"]
        print(f"documents==========={source_documents}")
        
        # 把大模型的回答结果返回网页进行渲染
        # return jsonify(refined_answer)
        return {"query": question, "result": result["result"]}
        # return render_template('index_opt.html', result=result)
    
    return render_template('index_opt.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=False,use_reloader=False,port=5000)