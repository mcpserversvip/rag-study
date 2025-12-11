"""
RAG知识库构建模块
整合PDF解析结果和MySQL数据,构建向量索引
"""
import os
from pathlib import Path
from typing import List, Optional
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Document
)
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.llms.openai_like import OpenAILike

from src.config import settings
from src.utils.logger import logger


class KnowledgeBuilder:
    """知识库构建器"""
    
    def __init__(self):
        """初始化知识库构建器"""
        # 设置API密钥
        os.environ['DASHSCOPE_API_KEY'] = settings.dashscope_api_key
        
        # 初始化embedding模型
        self.embed_model = DashScopeEmbedding(
            model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2
        )
        
        # 初始化LLM
        self.llm = OpenAILike(
            model=settings.llm_model,
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=settings.dashscope_api_key,
            is_chat_model=True
        )
    
    def load_documents_from_directory(self, directory: str) -> List[Document]:
        """
        从目录加载文档
        
        Args:
            directory: 文档目录路径
            
        Returns:
            Document对象列表
        """
        logger.info(f"从目录加载文档: {directory}")
        
        try:
            reader = SimpleDirectoryReader(directory)
            documents = reader.load_data()
            logger.success(f"成功加载 {len(documents)} 个文档")
            return documents
        except Exception as e:
            logger.error(f"加载文档失败: {e}")
            return []
    
    def create_documents_from_parsed_pdf(self, parsed_results: List[dict], pdf_name: str) -> List[Document]:
        """
        从PDF解析结果创建Document对象
        
        Args:
            parsed_results: PDF解析结果列表
            pdf_name: PDF文件名
            
        Returns:
            Document对象列表
        """
        documents = []
        
        for result in parsed_results:
            doc = Document(
                text=result['content'],
                metadata={
                    "source": pdf_name,
                    "page": result['page_num'],
                    "type": "medical_guideline"
                }
            )
            documents.append(doc)
        
        logger.info(f"从 {pdf_name} 创建了 {len(documents)} 个文档")
        return documents
    
    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """
        创建向量索引
        
        Args:
            documents: Document对象列表
            
        Returns:
            VectorStoreIndex对象
        """
        logger.info(f"开始创建向量索引,文档数: {len(documents)}")
        
        try:
            index = VectorStoreIndex.from_documents(
                documents,
                embed_model=self.embed_model,
                show_progress=True
            )
            logger.success("向量索引创建成功")
            return index
        except Exception as e:
            logger.error(f"创建向量索引失败: {e}")
            raise
    
    def persist_index(self, index: VectorStoreIndex, persist_dir: str):
        """
        持久化索引
        
        Args:
            index: VectorStoreIndex对象
            persist_dir: 持久化目录
        """
        logger.info(f"持久化索引到: {persist_dir}")
        
        try:
            Path(persist_dir).mkdir(parents=True, exist_ok=True)
            index.storage_context.persist(persist_dir)
            logger.success(f"索引已保存到: {persist_dir}")
        except Exception as e:
            logger.error(f"持久化索引失败: {e}")
            raise
    
    def load_index(self, persist_dir: str) -> Optional[VectorStoreIndex]:
        """
        加载已保存的索引
        
        Args:
            persist_dir: 索引目录
            
        Returns:
            VectorStoreIndex对象,如果加载失败返回None
        """
        logger.info(f"从目录加载索引: {persist_dir}")
        
        try:
            if not Path(persist_dir).exists():
                logger.warning(f"索引目录不存在: {persist_dir}")
                return None
            
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(
                storage_context,
                embed_model=self.embed_model
            )
            logger.success("索引加载成功")
            return index
        except Exception as e:
            logger.error(f"加载索引失败: {e}")
            return None
    
    def build_knowledge_base(
        self,
        parsed_pdf_results: dict,
        persist_dir: str,
        additional_docs_dir: Optional[str] = None
    ) -> VectorStoreIndex:
        """
        构建完整的知识库
        
        Args:
            parsed_pdf_results: PDF解析结果字典 {pdf_name: parsed_results}
            persist_dir: 持久化目录
            additional_docs_dir: 额外文档目录(可选)
            
        Returns:
            VectorStoreIndex对象
        """
        logger.info("开始构建医疗知识库")
        
        all_documents = []
        
        # 1. 从PDF解析结果创建文档
        for pdf_name, parsed_results in parsed_pdf_results.items():
            docs = self.create_documents_from_parsed_pdf(parsed_results, pdf_name)
            all_documents.extend(docs)
        
        # 2. 加载额外文档(如果有)
        if additional_docs_dir and Path(additional_docs_dir).exists():
            additional_docs = self.load_documents_from_directory(additional_docs_dir)
            all_documents.extend(additional_docs)
        
        logger.info(f"总文档数: {len(all_documents)}")
        
        # 3. 创建索引
        index = self.create_index(all_documents)
        
        # 4. 持久化索引
        self.persist_index(index, persist_dir)
        
        logger.success("医疗知识库构建完成")
        return index


def get_knowledge_builder() -> KnowledgeBuilder:
    """获取知识库构建器实例"""
    return KnowledgeBuilder()


if __name__ == "__main__":
    # 测试知识库构建
    builder = get_knowledge_builder()
    
    # 测试加载现有索引
    test_persist_dir = settings.knowledge_base_path
    
    index = builder.load_index(test_persist_dir)
    
    if index:
        logger.success("✅ 知识库加载成功")
    else:
        logger.info("知识库不存在,需要先运行构建脚本")
