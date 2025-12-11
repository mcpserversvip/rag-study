"""
多模态PDF解析器
使用阿里云多模态模型(qwen-vl-plus)解析PDF文档中的图文内容
"""
import base64
from pathlib import Path
from typing import List, Dict, Optional
from io import BytesIO

from pdf2image import convert_from_path
from PIL import Image
import dashscope
from dashscope import MultiModalConversation

from src.config import settings
from src.utils.logger import logger


class MultimodalPDFParser:
    """多模态PDF解析器"""
    
    def __init__(self):
        """初始化解析器"""
        # 设置API密钥
        dashscope.api_key = settings.dashscope_api_key
        self.model = settings.multimodal_model
        
    def pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[Image.Image]:
        """
        将PDF转换为图片列表
        
        Args:
            pdf_path: PDF文件路径
            dpi: 图片分辨率
            
        Returns:
            PIL Image对象列表
        """
        logger.info(f"开始转换PDF为图片: {pdf_path}, DPI={dpi}")
        
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            logger.success(f"PDF转换成功,共{len(images)}页")
            return images
        except Exception as e:
            logger.error(f"PDF转换失败: {e}")
            raise
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        将PIL Image转换为base64编码
        
        Args:
            image: PIL Image对象
            
        Returns:
            base64编码字符串
        """
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def parse_image_with_multimodal(
        self, 
        image: Image.Image, 
        prompt: str = "请详细描述这张医疗指南图片中的所有内容,包括文字、表格、图表等。请保持原文的专业性和准确性。"
    ) -> str:
        """
        使用多模态模型解析图片内容
        
        Args:
            image: PIL Image对象
            prompt: 提示词
            
        Returns:
            解析结果文本
        """
        try:
            # 将图片转换为base64
            image_base64 = self.image_to_base64(image)
            
            # 调用多模态模型
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": image_base64},
                        {"text": prompt}
                    ]
                }
            ]
            
            response = MultiModalConversation.call(
                model=self.model,
                messages=messages
            )
            
            if response.status_code == 200:
                result = response.output.choices[0].message.content[0]["text"]
                return result
            else:
                logger.error(f"多模态模型调用失败: {response.code}, {response.message}")
                return ""
                
        except Exception as e:
            logger.error(f"图片解析失败: {e}")
            return ""
    
    def parse_pdf(
        self, 
        pdf_path: str, 
        output_dir: Optional[str] = None,
        dpi: int = 200,
        custom_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        解析PDF文档
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录(可选,用于保存中间图片)
            dpi: 图片分辨率
            custom_prompt: 自定义提示词
            
        Returns:
            解析结果列表,每个元素包含page_num和content
        """
        logger.info(f"开始解析PDF: {pdf_path}")
        
        # 转换PDF为图片
        images = self.pdf_to_images(pdf_path, dpi=dpi)
        
        # 如果指定了输出目录,保存图片
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            pdf_name = Path(pdf_path).stem
            
            for i, img in enumerate(images, 1):
                img_path = output_path / f"{pdf_name}_page_{i}.png"
                img.save(img_path)
                logger.debug(f"保存图片: {img_path}")
        
        # 解析每一页
        results = []
        prompt = custom_prompt or "请详细描述这张医疗指南图片中的所有内容,包括文字、表格、图表、诊断标准、治疗方案等。请保持原文的专业性和准确性,特别注意数值、剂量、诊断标准等关键信息。"
        
        for i, image in enumerate(images, 1):
            logger.info(f"正在解析第 {i}/{len(images)} 页...")
            
            content = self.parse_image_with_multimodal(image, prompt)
            
            if content:
                results.append({
                    "page_num": i,
                    "content": content
                })
                logger.success(f"第 {i} 页解析成功,内容长度: {len(content)}")
            else:
                logger.warning(f"第 {i} 页解析失败或内容为空")
        
        logger.success(f"PDF解析完成,成功解析 {len(results)}/{len(images)} 页")
        return results
    
    def save_parsed_results(self, results: List[Dict[str, str]], output_file: str):
        """
        保存解析结果到文本文件
        
        Args:
            results: 解析结果列表
            output_file: 输出文件路径
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"{'='*80}\n")
                f.write(f"第 {result['page_num']} 页\n")
                f.write(f"{'='*80}\n\n")
                f.write(result['content'])
                f.write("\n\n")
        
        logger.success(f"解析结果已保存到: {output_path}")


def get_pdf_parser() -> MultimodalPDFParser:
    """获取PDF解析器实例"""
    return MultimodalPDFParser()


if __name__ == "__main__":
    # 测试PDF解析
    parser = get_pdf_parser()
    
    # 测试文件
    test_pdf = "/Users/xiaoyubin/Desktop/mcpserversvip/rag-study/data/高血压诊疗指南.pdf"
    
    if Path(test_pdf).exists():
        logger.info(f"测试PDF文件: {test_pdf}")
        
        # 解析PDF(只解析前2页作为测试)
        results = parser.parse_pdf(
            pdf_path=test_pdf,
            output_dir="./temp/pdf_images",
            dpi=150  # 测试时使用较低分辨率
        )
        
        # 保存结果
        if results:
            parser.save_parsed_results(
                results[:2],  # 只保存前2页
                output_file="./temp/parsed_results.txt"
            )
    else:
        logger.error(f"测试文件不存在: {test_pdf}")
