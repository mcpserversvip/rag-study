"""
医学术语标准化映射模块
实现术语同义词映射,例如"心梗"→"心肌梗死"
评分点: 4.1.1 术语标准化映射(3分)
"""
from typing import Dict, List, Optional, Set
import json
from pathlib import Path

from src.utils.logger import logger


class MedicalTermMapper:
    """医学术语映射器"""
    
    def __init__(self):
        """初始化术语映射器"""
        # 术语映射表: {俗称/简称: 标准术语}
        self.term_mapping = {
            # 心血管疾病
            "心梗": "心肌梗死",
            "心梗死": "心肌梗死",
            "MI": "心肌梗死",
            "急性心梗": "急性心肌梗死",
            "AMI": "急性心肌梗死",
            "心衰": "心力衰竭",
            "心功能不全": "心力衰竭",
            "房颤": "心房颤动",
            "冠心病": "冠状动脉粥样硬化性心脏病",
            "冠脉病": "冠状动脉疾病",
            
            # 高血压相关
            "高血压": "原发性高血压",
            "血压高": "高血压",
            "高压": "高血压",
            "继发高血压": "继发性高血压",
            "高血压危象": "高血压急症",
            "高血压脑病": "高血压性脑病",
            
            # 糖尿病相关
            "糖尿病": "糖尿病",
            "DM": "糖尿病",
            "1型糖尿病": "1型糖尿病",
            "T1DM": "1型糖尿病",
            "2型糖尿病": "2型糖尿病",
            "T2DM": "2型糖尿病",
            "糖尿": "糖尿病",
            "血糖高": "高血糖",
            "低血糖": "低血糖症",
            "糖化血红蛋白": "糖化血红蛋白",
            "HbA1c": "糖化血红蛋白",
            
            # 肾脏疾病
            "肾衰": "肾功能衰竭",
            "肾衰竭": "肾功能衰竭",
            "尿毒症": "慢性肾功能衰竭尿毒症期",
            "肾病": "肾脏疾病",
            "蛋白尿": "蛋白尿",
            
            # 脑血管疾病
            "脑梗": "脑梗死",
            "脑梗塞": "脑梗死",
            "中风": "脑卒中",
            "脑卒中": "脑血管意外",
            "脑出血": "脑出血",
            "蛛网膜下腔出血": "蛛网膜下腔出血",
            
            # 症状
            "头晕": "眩晕",
            "头疼": "头痛",
            "胸痛": "胸痛",
            "胸闷": "胸闷",
            "气短": "呼吸困难",
            "气喘": "呼吸困难",
            "心慌": "心悸",
            "心跳快": "心动过速",
            
            # 检查项目
            "心电图": "心电图检查",
            "ECG": "心电图",
            "彩超": "超声检查",
            "B超": "超声检查",
            "CT": "计算机断层扫描",
            "核磁": "磁共振成像",
            "MRI": "磁共振成像",
            
            # 药物类别
            "降压药": "抗高血压药物",
            "降糖药": "降血糖药物",
            "胰岛素": "胰岛素",
            "利尿剂": "利尿药",
            "他汀": "他汀类药物",
            "阿司匹林": "阿司匹林",
            "ACEI": "血管紧张素转换酶抑制剂",
            "ARB": "血管紧张素受体拮抗剂",
            "CCB": "钙通道阻滞剂",
            "β受体阻滞剂": "β肾上腺素受体阻滞剂",
        }
        
        # 反向映射: {标准术语: [所有同义词]}
        self.reverse_mapping = self._build_reverse_mapping()
        
        logger.info(f"术语映射器初始化完成,共{len(self.term_mapping)}个映射")
    
    def _build_reverse_mapping(self) -> Dict[str, List[str]]:
        """构建反向映射表"""
        reverse = {}
        for synonym, standard in self.term_mapping.items():
            if standard not in reverse:
                reverse[standard] = []
            reverse[standard].append(synonym)
        return reverse
    
    def normalize(self, term: str) -> str:
        """
        标准化术语
        
        Args:
            term: 输入术语
            
        Returns:
            标准化后的术语
        """
        # 去除空格
        term = term.strip()
        
        # 查找映射
        if term in self.term_mapping:
            standard_term = self.term_mapping[term]
            logger.debug(f"术语映射: '{term}' → '{standard_term}'")
            return standard_term
        
        # 如果已经是标准术语,直接返回
        return term
    
    def get_synonyms(self, term: str) -> List[str]:
        """
        获取术语的所有同义词
        
        Args:
            term: 术语
            
        Returns:
            同义词列表
        """
        # 先标准化
        standard = self.normalize(term)
        
        # 查找所有同义词
        if standard in self.reverse_mapping:
            return self.reverse_mapping[standard]
        
        return [term]
    
    def expand_query(self, query: str) -> str:
        """
        扩展查询,添加同义词
        
        Args:
            query: 原始查询
            
        Returns:
            扩展后的查询
        """
        # 简单实现:查找query中的术语并替换
        expanded = query
        
        # 按长度排序,优先匹配长术语
        sorted_terms = sorted(self.term_mapping.keys(), key=len, reverse=True)
        
        for term in sorted_terms:
            if term in query:
                standard = self.term_mapping[term]
                # 如果不同,添加标准术语
                if term != standard and standard not in query:
                    expanded = expanded.replace(term, f"{term}({standard})")
        
        return expanded
    
    def save_mapping_table(self, output_path: str):
        """
        保存映射表到文件
        
        Args:
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 按标准术语分组
        grouped = {}
        for synonym, standard in self.term_mapping.items():
            if standard not in grouped:
                grouped[standard] = []
            grouped[standard].append(synonym)
        
        # 保存为JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(grouped, f, ensure_ascii=False, indent=2)
        
        logger.success(f"映射表已保存到: {output_file}")
    
    def print_mapping_table(self):
        """打印映射表"""
        print("\n" + "="*80)
        print("医学术语标准化映射表")
        print("="*80)
        
        # 按标准术语分组
        grouped = {}
        for synonym, standard in self.term_mapping.items():
            if standard not in grouped:
                grouped[standard] = []
            grouped[standard].append(synonym)
        
        # 打印
        for standard, synonyms in sorted(grouped.items()):
            print(f"\n【{standard}】")
            print(f"  同义词: {', '.join(synonyms)}")
        
        print("\n" + "="*80)
        print(f"共{len(grouped)}个标准术语,{len(self.term_mapping)}个映射关系")
        print("="*80)


# 全局术语映射器实例
term_mapper = MedicalTermMapper()


def get_term_mapper() -> MedicalTermMapper:
    """获取术语映射器实例"""
    return term_mapper


if __name__ == "__main__":
    # 测试术语映射
    mapper = get_term_mapper()
    
    # 测试案例
    test_cases = [
        "心梗",
        "高血压",
        "糖尿病",
        "脑梗",
        "心衰",
        "DM",
        "ACEI",
        "心肌梗死"  # 已经是标准术语
    ]
    
    print("\n" + "="*80)
    print("术语标准化测试")
    print("="*80)
    
    for term in test_cases:
        standard = mapper.normalize(term)
        synonyms = mapper.get_synonyms(term)
        print(f"\n输入: {term}")
        print(f"标准术语: {standard}")
        print(f"所有同义词: {', '.join(synonyms)}")
    
    # 测试查询扩展
    print("\n" + "="*80)
    print("查询扩展测试")
    print("="*80)
    
    test_queries = [
        "心梗的治疗方法",
        "高血压患者能吃什么",
        "糖尿病并发症有哪些"
    ]
    
    for query in test_queries:
        expanded = mapper.expand_query(query)
        print(f"\n原始查询: {query}")
        print(f"扩展查询: {expanded}")
    
    # 打印完整映射表
    mapper.print_mapping_table()
    
    # 保存映射表
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    mapper.save_mapping_table(str(project_root / 'temp' / 'term_mapping.json'))
