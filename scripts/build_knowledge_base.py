"""
知识库构建脚本
解析PDF文档并构建RAG向量索引
"""
import sys
import os
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.pdf_parser import get_pdf_parser
from src.rag import get_knowledge_builder
from src.utils.logger import logger


def parse_pdfs(pdf_dir: str, output_dir: str, use_cache: bool = True):
    """
    解析PDF文档
    
    Args:
        pdf_dir: PDF文件目录
        output_dir: 解析结果输出目录
        use_cache: 是否使用缓存的解析结果
        
    Returns:
        解析结果字典 {pdf_name: parsed_results}
    """
    logger.info(f"解析PDF文档: {pdf_dir}")
    
    pdf_path = Path(pdf_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not pdf_path.exists():
        logger.error(f"PDF目录不存在: {pdf_dir}")
        return {}
    
    # 获取所有PDF文件
    pdf_files = list(pdf_path.glob('*.pdf'))
    logger.info(f"找到 {len(pdf_files)} 个PDF文件")
    
    parser = get_pdf_parser()
    all_results = {}
    
    for pdf_file in pdf_files:
        pdf_name = pdf_file.stem
        cache_file = output_path / f"{pdf_name}_parsed.json"
        
        # 检查缓存
        if use_cache and cache_file.exists():
            logger.info(f"使用缓存: {pdf_name}")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                all_results[pdf_name] = results
                logger.success(f"  ✅ 从缓存加载 {len(results)} 页")
                continue
            except Exception as e:
                logger.warning(f"  缓存加载失败: {e}, 重新解析")
        
        # 解析PDF
        logger.info(f"解析PDF: {pdf_name}")
        try:
            results = parser.parse_pdf(
                pdf_path=str(pdf_file),
                output_dir=str(output_path / f"{pdf_name}_images"),
                dpi=200  # 使用200 DPI以平衡质量和速度
            )
            
            if results:
                all_results[pdf_name] = results
                
                # 保存解析结果到缓存
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.success(f"  ✅ 解析完成,共 {len(results)} 页")
                
                # 保存为文本文件
                text_file = output_path / f"{pdf_name}_parsed.txt"
                parser.save_parsed_results(results, str(text_file))
            else:
                logger.warning(f"  ⚠️ 解析结果为空")
                
        except Exception as e:
            logger.error(f"  ❌ 解析失败: {e}")
    
    return all_results


def build_knowledge_base(parsed_results: dict, persist_dir: str):
    """
    构建知识库
    
    Args:
        parsed_results: PDF解析结果
        persist_dir: 知识库持久化目录
    """
    logger.info("构建RAG知识库...")
    
    if not parsed_results:
        logger.error("没有PDF解析结果,无法构建知识库")
        return
    
    try:
        builder = get_knowledge_builder()
        
        # 构建知识库
        index = builder.build_knowledge_base(
            parsed_pdf_results=parsed_results,
            persist_dir=persist_dir
        )
        
        logger.success(f"✅ 知识库构建完成,已保存到: {persist_dir}")
        
        # 测试查询
        logger.info("测试知识库查询...")
        from src.rag import create_query_engine
        
        query_engine = create_query_engine(index)
        test_question = "糖尿病的诊断标准是什么?"
        
        logger.info(f"测试问题: {test_question}")
        result = query_engine.query(test_question)
        
        print("\n" + "="*80)
        print("测试查询结果:")
        print("="*80)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ 知识库构建失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始构建医疗知识库")
    logger.info("="*80)
    
    # 配置路径
    pdf_dir = project_root / 'data'
    parsed_output_dir = project_root / 'temp' / 'parsed_pdfs'
    knowledge_base_dir = settings.knowledge_base_path
    
    logger.info(f"PDF目录: {pdf_dir}")
    logger.info(f"解析结果目录: {parsed_output_dir}")
    logger.info(f"知识库目录: {knowledge_base_dir}")
    
    # 1. 解析PDF文档
    logger.info("\n步骤1: 解析PDF文档")
    logger.info("-"*80)
    
    parsed_results = parse_pdfs(
        pdf_dir=str(pdf_dir),
        output_dir=str(parsed_output_dir),
        use_cache=True  # 使用缓存以节省API调用
    )
    
    if not parsed_results:
        logger.error("PDF解析失败,无法继续")
        return
    
    logger.info(f"\n解析完成,共处理 {len(parsed_results)} 个PDF文件")
    for pdf_name, results in parsed_results.items():
        logger.info(f"  - {pdf_name}: {len(results)} 页")
    
    # 2. 构建知识库
    logger.info("\n步骤2: 构建RAG知识库")
    logger.info("-"*80)
    
    build_knowledge_base(
        parsed_results=parsed_results,
        persist_dir=knowledge_base_dir
    )
    
    logger.success("\n" + "="*80)
    logger.success("✅ 医疗知识库构建完成!")
    logger.success("="*80)
    logger.info("\n下一步: 运行 'uv run python src/app.py' 启动Web应用")


if __name__ == "__main__":
    main()
