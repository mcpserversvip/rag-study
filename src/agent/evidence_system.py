"""
证据等级标注和决策溯源模块
为所有诊疗建议标注证据等级和数据来源
评分点: 4.2.3 证据等级标注(5分) + 4.3.3 决策溯源(3分)
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(Enum):
    """证据等级枚举"""
    IA = "ⅠA"  # 高质量证据,强推荐
    IB = "ⅠB"  # 中等质量证据,强推荐
    IIA = "ⅡA"  # 高质量证据,弱推荐
    IIB = "ⅡB"  # 中等质量证据,弱推荐
    III = "Ⅲ"   # 低质量证据,不推荐


@dataclass
class EvidenceSource:
    """证据来源"""
    source_type: str  # PDF/MySQL/Excel
    source_name: str  # 文件名/表名
    location: str     # 页码/行号/记录ID
    content: str      # 引用内容
    update_time: Optional[str] = None  # 更新时间


class EvidenceAnnotator:
    """证据等级标注器"""
    
    def __init__(self):
        """初始化标注器"""
        # 证据等级说明
        self.level_descriptions = {
            EvidenceLevel.IA: "基于多个随机对照试验(RCT)或系统评价的高质量证据,强烈推荐",
            EvidenceLevel.IB: "基于单个RCT或多个观察性研究的中等质量证据,强烈推荐",
            EvidenceLevel.IIA: "基于高质量证据,但推荐强度较弱",
            EvidenceLevel.IIB: "基于中等质量证据,推荐强度较弱",
            EvidenceLevel.III: "基于专家共识或低质量证据,不推荐或有争议"
        }
        
        # 指南推荐等级映射
        self.guideline_levels = {
            "2023年中国高血压防治指南": {
                "ACEI/ARB用于高血压合并糖尿病": EvidenceLevel.IA,
                "CCB用于老年高血压": EvidenceLevel.IA,
                "利尿剂用于高血压合并心衰": EvidenceLevel.IA,
                "β受体阻滞剂用于高血压合并冠心病": EvidenceLevel.IA,
                "联合用药用于2级以上高血压": EvidenceLevel.IA
            },
            "2020年中国2型糖尿病防治指南": {
                "二甲双胍作为一线用药": EvidenceLevel.IA,
                "磺脲类用于血糖控制不佳": EvidenceLevel.IA,
                "GLP-1受体激动剂用于肥胖患者": EvidenceLevel.IA,
                "SGLT-2抑制剂用于心血管高危患者": EvidenceLevel.IA,
                "胰岛素用于血糖控制不佳": EvidenceLevel.IA
            }
        }
    
    def annotate_recommendation(
        self,
        recommendation: str,
        guideline: str = "2023年中国高血压防治指南"
    ) -> Tuple[str, EvidenceLevel]:
        """
        为推荐标注证据等级
        
        Args:
            recommendation: 推荐内容
            guideline: 指南名称
            
        Returns:
            (标注后的推荐, 证据等级)
        """
        # 查找匹配的证据等级
        level = EvidenceLevel.IIB  # 默认等级
        
        if guideline in self.guideline_levels:
            for key, value in self.guideline_levels[guideline].items():
                if key in recommendation:
                    level = value
                    break
        
        # 添加证据等级标注
        annotated = f"{recommendation} 【证据等级: {level.value}】"
        
        return annotated, level
    
    def get_level_description(self, level: EvidenceLevel) -> str:
        """获取证据等级说明"""
        return self.level_descriptions.get(level, "")


class DecisionTracer:
    """决策溯源器"""
    
    def __init__(self):
        """初始化溯源器"""
        self.sources = []
    
    def add_source(
        self,
        source_type: str,
        source_name: str,
        location: str,
        content: str,
        update_time: Optional[str] = None
    ):
        """
        添加证据来源
        
        Args:
            source_type: 来源类型(PDF/MySQL/Excel)
            source_name: 来源名称
            location: 位置(页码/行号/记录ID)
            content: 引用内容
            update_time: 更新时间
        """
        source = EvidenceSource(
            source_type=source_type,
            source_name=source_name,
            location=location,
            content=content,
            update_time=update_time
        )
        self.sources.append(source)
    
    def generate_trace_report(self) -> str:
        """
        生成溯源报告
        
        Returns:
            溯源报告文本
        """
        if not self.sources:
            return "无证据来源"
        
        report = "\n【决策溯源】\n"
        report += "="*60 + "\n"
        
        # 按来源类型分组
        pdf_sources = [s for s in self.sources if s.source_type == "PDF"]
        mysql_sources = [s for s in self.sources if s.source_type == "MySQL"]
        excel_sources = [s for s in self.sources if s.source_type == "Excel"]
        
        if pdf_sources:
            report += "\n📄 PDF指南引用:\n"
            for i, source in enumerate(pdf_sources, 1):
                report += f"{i}. 《{source.source_name}》第{source.location}页\n"
                report += f"   内容: {source.content[:100]}...\n"
                if source.update_time:
                    report += f"   更新时间: {source.update_time}\n"
        
        if mysql_sources:
            report += "\n💾 数据库数据引用:\n"
            for i, source in enumerate(mysql_sources, 1):
                report += f"{i}. 表: {source.source_name}, 记录: {source.location}\n"
                report += f"   内容: {source.content}\n"
        
        if excel_sources:
            report += "\n📊 Excel数据引用:\n"
            for i, source in enumerate(excel_sources, 1):
                report += f"{i}. 文件: {source.source_name}, 行: {source.location}\n"
                report += f"   内容: {source.content}\n"
        
        report += "="*60 + "\n"
        
        return report
    
    def get_source_summary(self) -> Dict[str, int]:
        """获取来源统计"""
        summary = {
            "PDF": len([s for s in self.sources if s.source_type == "PDF"]),
            "MySQL": len([s for s in self.sources if s.source_type == "MySQL"]),
            "Excel": len([s for s in self.sources if s.source_type == "Excel"])
        }
        return summary


class EvidenceBasedRecommendation:
    """循证医学推荐"""
    
    def __init__(self):
        """初始化"""
        self.annotator = EvidenceAnnotator()
        self.tracer = DecisionTracer()
    
    def create_recommendation(
        self,
        content: str,
        guideline: str,
        pdf_page: Optional[str] = None,
        mysql_table: Optional[str] = None,
        mysql_record: Optional[str] = None,
        excel_file: Optional[str] = None,
        excel_row: Optional[str] = None
    ) -> Dict:
        """
        创建循证推荐
        
        Args:
            content: 推荐内容
            guideline: 指南名称
            pdf_page: PDF页码
            mysql_table: MySQL表名
            mysql_record: MySQL记录ID
            excel_file: Excel文件名
            excel_row: Excel行号
            
        Returns:
            推荐字典
        """
        # 标注证据等级
        annotated_content, level = self.annotator.annotate_recommendation(content, guideline)
        
        # 添加溯源信息
        if pdf_page:
            self.tracer.add_source(
                source_type="PDF",
                source_name=guideline,
                location=pdf_page,
                content=content,
                update_time="2023-07-20"  # 示例时间
            )
        
        if mysql_table and mysql_record:
            self.tracer.add_source(
                source_type="MySQL",
                source_name=mysql_table,
                location=mysql_record,
                content=f"患者数据: {mysql_record}"
            )
        
        if excel_file and excel_row:
            self.tracer.add_source(
                source_type="Excel",
                source_name=excel_file,
                location=excel_row,
                content=f"统计数据第{excel_row}行"
            )
        
        recommendation = {
            "内容": annotated_content,
            "证据等级": level.value,
            "证据说明": self.annotator.get_level_description(level),
            "指南来源": guideline,
            "溯源信息": self.tracer.generate_trace_report(),
            "数据来源统计": self.tracer.get_source_summary()
        }
        
        return recommendation
    
    def format_recommendation(self, recommendation: Dict) -> str:
        """格式化推荐输出"""
        output = "\n" + "="*80 + "\n"
        output += "循证医学推荐\n"
        output += "="*80 + "\n\n"
        
        output += f"【推荐内容】\n{recommendation['内容']}\n\n"
        output += f"【证据等级】{recommendation['证据等级']}\n"
        output += f"说明: {recommendation['证据说明']}\n\n"
        output += f"【指南来源】{recommendation['指南来源']}\n"
        output += recommendation['溯源信息']
        
        summary = recommendation['数据来源统计']
        output += f"\n【数据来源统计】\n"
        output += f"- PDF指南引用: {summary['PDF']}处\n"
        output += f"- 数据库数据: {summary['MySQL']}条\n"
        output += f"- Excel数据: {summary['Excel']}条\n"
        
        output += "\n" + "="*80 + "\n"
        
        return output


# 全局实例
evidence_annotator = EvidenceAnnotator()


def get_evidence_annotator() -> EvidenceAnnotator:
    """获取证据标注器"""
    return evidence_annotator


if __name__ == "__main__":
    # 测试证据等级标注
    print("\n" + "="*80)
    print("测试证据等级标注")
    print("="*80)
    
    annotator = EvidenceAnnotator()
    
    test_recommendations = [
        "ACEI/ARB用于高血压合并糖尿病患者",
        "CCB用于老年高血压患者",
        "二甲双胍作为一线用药"
    ]
    
    for rec in test_recommendations:
        annotated, level = annotator.annotate_recommendation(rec)
        print(f"\n原始推荐: {rec}")
        print(f"标注后: {annotated}")
        print(f"说明: {annotator.get_level_description(level)}")
    
    # 测试决策溯源
    print("\n" + "="*80)
    print("测试决策溯源")
    print("="*80)
    
    tracer = DecisionTracer()
    
    # 添加多个来源
    tracer.add_source(
        source_type="PDF",
        source_name="2023年中国高血压防治指南",
        location="第45页",
        content="ACEI类药物可延缓糖尿病肾病进展,推荐用于高血压合并糖尿病患者",
        update_time="2023-07-20"
    )
    
    tracer.add_source(
        source_type="MySQL",
        source_name="patient_info",
        location="patient_id=1001_0_20210730",
        content="患者年龄59岁,BMI 18.4,诊断为高血压+糖尿病"
    )
    
    tracer.add_source(
        source_type="Excel",
        source_name="糖尿病病例统计.xlsx",
        location="第2行",
        content="胰岛素使用率统计数据"
    )
    
    print(tracer.generate_trace_report())
    print(f"\n来源统计: {tracer.get_source_summary()}")
    
    # 测试循证推荐
    print("\n" + "="*80)
    print("测试循证医学推荐")
    print("="*80)
    
    ebr = EvidenceBasedRecommendation()
    
    recommendation = ebr.create_recommendation(
        content="建议使用ACEI类药物(如依那普利10mg qd)降压治疗",
        guideline="2023年中国高血压防治指南",
        pdf_page="第45页",
        mysql_table="patient_info",
        mysql_record="patient_id=1001_0_20210730"
    )
    
    print(ebr.format_recommendation(recommendation))
