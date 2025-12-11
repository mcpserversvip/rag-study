'''欢迎来到联通大模型开发框架实战课

作者 杨勇'''

import os

# 1.Load 导入Document Loaders
#from langchain.document_loaders import PyPDFLoader
#from langchain.document_loaders import Docx2txtLoader
#from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader


# 加载Documents
base_dir = './data' # 文档的存放目录，存放企业很多文档
documents = []
for file in os.listdir(base_dir): 
    # 构建完整的文件路径
    file_path = os.path.join(base_dir, file)
    if file.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith('.txt'):
        loader = TextLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith('.md'):
        loader = UnstructuredMarkdownLoader(file_path,mode="elements")
        documents.extend(loader.load())

# 2.Split 将Documents切分成块以便后续进行嵌入和向量存储
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_community.vectorstores import FAISS  # 向量数据库
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
chunked_documents = text_splitter.split_documents(documents)

# 3.Store 将分割嵌入并存储在矢量数据库Qdrant中
#from langchain.vectorstores import Qdrant
from langchain_community.vectorstores import Qdrant
#from langchain.embeddings import OpenAIEmbeddings
# 定义向量模型路径
EMBEDDING_MODEL = '/root/autodl-tmp/m3e-base'

vectorstore = Qdrant.from_documents(
    # 以分块的文档
    documents=chunked_documents,
    # 初始化huggingface模型embedding
    embedding=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL),
    location=":memory:",  # in-memory 存储
    collection_name="my_documents",) # 指定collection_name

# 4. Retrieval 准备模型和Retrieval链
import logging # 导入Logging工具
from langchain.chat_models import ChatOpenAI # ChatOpenAI模型
from langchain.retrievers.multi_query import MultiQueryRetriever # MultiQueryRetriever工具
from langchain.chains import RetrievalQA # RetrievalQA链

# 设置Logging
logging.basicConfig()
logging.getLogger('langchain.retrievers.multi_query').setLevel(logging.DEBUG)

# 实例化一个本地大模型工具 - glm3
from langchain.llms.base import LLM
from typing import Any, List, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from transformers import AutoTokenizer, AutoModelForCausalLM

class ChatGLM_LLM(LLM):
    # 基于本地 InternLM 自定义 LLM 类
    tokenizer : AutoTokenizer = None
    model: AutoModelForCausalLM = None

    def __init__(self, model_path :str):
        # model_path: InternLM 模型路径
        # 从本地初始化模型
        super().__init__()
        print("正在从本地加载模型...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).to(torch.bfloat16).cuda()
        #self.model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).to(torch.bfloat16).cuda().quantize(8)
        self.model = self.model.eval()
        print("完成本地模型的加载")

    def _call(self, prompt : str, stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any):
        # 重写调用函数
        print(f"LLM prompt:{prompt}")
        response, history = self.model.chat(self.tokenizer, prompt , history=[], temperature=0.3)
        return response
        
    @property
    def _llm_type(self) -> str:
        return "ChatGLM3-6B"

import torch
llm = ChatGLM_LLM(model_path = "/root/autodl-tmp/chatglm3-6b")

# 实例化一个MultiQueryRetriever
retriever_from_llm = MultiQueryRetriever.from_llm(retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), llm=llm)

# 实例化一个RetrievalQA链
qa_chain = RetrievalQA.from_chain_type(llm,retriever=retriever_from_llm, return_source_documents=True)

# 5. Output 问答系统的UI实现
from flask import Flask, request, jsonify, render_template
app = Flask(__name__) # Flask APP

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        # 接收用户输入作为问题
        question = request.form.get('question')        
        
        # RetrievalQA链 - 读入问题，生成答案
        result = qa_chain({"query": question})
        source_documents = result["source_documents"]
        print(f"documents==========={source_documents}")
        
        # 把大模型的回答结果返回网页进行渲染
        # return jsonify(refined_answer)
        return {"query": question, "result": result["result"]}
        # return render_template('index_opt.html', result=result)
    
    return render_template('index_opt.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=False,use_reloader=False,port=5000)