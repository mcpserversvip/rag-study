"""
RAG查询引擎模块
提供知识库检索和查询功能
"""
import os
from typing import Generator, Optional
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.llms.openai_like import OpenAILike

from src.config import settings
from src.utils.logger import logger
from src.rag.prompt_templates import get_template


class QueryEngine:
    """RAG查询引擎"""
    
    def __init__(self, index: VectorStoreIndex):
        """
        初始化查询引擎
        
        Args:
            index: VectorStoreIndex对象
        """
        self.index = index
        
        # 设置API密钥
        os.environ['DASHSCOPE_API_KEY'] = settings.dashscope_api_key
        
        # 创建查询引擎
        self._inner_query_engine = self._create_query_engine()
        
        # 设置默认的医疗QA模板（必须在 _inner_query_engine 赋值后调用）
        self.update_prompt_template(template_type="medical_qa")
    
    @property
    def query_engine(self):
        """获取内部查询引擎"""
        return self._inner_query_engine
    
    def _create_query_engine(self):
        """创建查询引擎"""
        logger.info("创建RAG查询引擎")
        
        query_engine = self.index.as_query_engine(
            streaming=True,
            llm=OpenAILike(
                model=settings.llm_model,
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key=settings.dashscope_api_key,
                is_chat_model=True
            ),
            similarity_top_k=5  # 返回最相关的5个文档片段
        )
        
        return query_engine
    
    def update_prompt_template(self, template_type: str = "medical_qa", custom_template: Optional[str] = None):
        """
        更新Prompt模板
        
        Args:
            template_type: 模板类型
            custom_template: 自定义模板(可选)
        """
        if custom_template:
            template_str = custom_template
        else:
            template_str = get_template(template_type)
        
        qa_prompt_tmpl = PromptTemplate(template_str)
        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
        )
        
        logger.info(f"Prompt模板已更新: {template_type}")
    
    def query(self, question: str) -> str:
        """
        同步查询
        
        Args:
            question: 问题
            
        Returns:
            回答文本
        """
        logger.info(f"查询问题: {question}")
        
        try:
            response = self.query_engine.query(question)
            
            # 收集流式响应
            full_response = ""
            for chunk in response.response_gen:
                full_response += chunk
            
            return full_response
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return f"查询出错: {str(e)}"
    
    def query_stream(self, question: str) -> Generator[str, None, None]:
        """
        流式查询
        
        Args:
            question: 问题
            
        Yields:
            回答文本片段
        """
        logger.info(f"流式查询问题: {question}")
        
        if not question:
            yield "错误:问题不能为空"
            return
        
        try:
            streaming_response = self.query_engine.query(question)
            
            for chunk in streaming_response.response_gen:
                yield chunk
                
        except Exception as e:
            logger.error(f"流式查询失败: {e}")
            yield f"查询出错: {str(e)}"
    
    def query_with_context(self, question: str, context: dict) -> Generator[str, None, None]:
        """
        带上下文的查询(用于患者评估等场景)
        
        Args:
            question: 问题
            context: 上下文信息字典
            
        Yields:
            回答文本片段
        """
        # 构建包含上下文的问题
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        full_question = f"{context_str}\n\n问题: {question}"
        
        yield from self.query_stream(full_question)


def create_query_engine(index: VectorStoreIndex) -> QueryEngine:
    """
    创建查询引擎
    
    Args:
        index: VectorStoreIndex对象
        
    Returns:
        QueryEngine对象
    """
    return QueryEngine(index)


if __name__ == "__main__":
    from src.rag.knowledge_builder import get_knowledge_builder
    
    # 测试查询引擎
    builder = get_knowledge_builder()
    index = builder.load_index(settings.knowledge_base_path)
    
    if index:
        logger.info("测试查询引擎")
        
        engine = create_query_engine(index)
        
        # 测试查询
        test_question = "糖尿病患者的血糖控制目标是什么?"
        
        logger.info(f"测试问题: {test_question}")
        
        print("\n" + "="*80)
        print("回答:")
        print("="*80)
        
        for chunk in engine.query_stream(test_question):
            print(chunk, end="", flush=True)
        
        print("\n" + "="*80)
    else:
        logger.error("知识库不存在,请先运行构建脚本")
