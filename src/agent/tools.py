"""
智能体工具集
为医疗决策智能体提供各种工具函数
"""
from typing import Dict, List, Any, Optional
import json

from src.database import get_medical_retriever
from src.rag import QueryEngine
from src.agent.safety_checker import get_safety_checker
from src.utils.logger import logger


class MedicalTools:
    """医疗决策工具集"""
    
    def __init__(self, query_engine: Optional[QueryEngine] = None):
        """
        初始化工具集
        
        Args:
            query_engine: RAG查询引擎(可选)
        """
        self.medical_retriever = get_medical_retriever()
        self.query_engine = query_engine
        self.safety_checker = get_safety_checker()
    
    def search_medical_guidelines(self, query: str) -> str:
        """
        搜索医疗指南
        
        Args:
            query: 查询问题
            
        Returns:
            指南内容
        """
        logger.info(f"搜索医疗指南: {query}")
        
        if not self.query_engine:
            return "RAG查询引擎未初始化"
        
        try:
            result = self.query_engine.query(query)
            return result
        except Exception as e:
            logger.error(f"搜索指南失败: {e}")
            return f"搜索失败: {str(e)}"
    
    def get_patient_information(self, patient_id: str) -> str:
        """
        获取患者信息
        
        Args:
            patient_id: 患者ID
            
        Returns:
            患者信息JSON字符串
        """
        logger.info(f"获取患者信息: {patient_id}")
        
        try:
            patient_info = self.medical_retriever.get_patient_info(patient_id)
            
            if patient_info:
                return json.dumps(patient_info, ensure_ascii=False, indent=2)
            else:
                return f"未找到患者ID: {patient_id}"
        except Exception as e:
            logger.error(f"获取患者信息失败: {e}")
            return f"获取失败: {str(e)}"
    
    def get_patient_comprehensive_data(self, patient_id: str) -> str:
        """
        获取患者综合数据
        
        Args:
            patient_id: 患者ID
            
        Returns:
            综合数据JSON字符串
        """
        logger.info(f"获取患者综合数据: {patient_id}")
        
        try:
            data = self.medical_retriever.get_patient_comprehensive_data(patient_id)
            return json.dumps(data, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"获取综合数据失败: {e}")
            return f"获取失败: {str(e)}"
    
    def assess_diabetes_risk(self, patient_id: str) -> str:
        """
        评估糖尿病风险
        
        Args:
            patient_id: 患者ID
            
        Returns:
            风险评估结果
        """
        logger.info(f"评估糖尿病风险: {patient_id}")
        
        try:
            # 获取患者信息
            patient_info = self.medical_retriever.get_patient_info(patient_id)
            if not patient_info:
                return f"未找到患者ID: {patient_id}"
            
            # 获取糖尿病评估记录
            diabetes_assessments = self.medical_retriever.get_diabetes_assessment(patient_id, limit=1)
            
            # 获取相关检验结果
            lab_results = self.medical_retriever.get_patient_lab_results(patient_id, limit=10)
            
            # 构建评估报告
            report = f"患者: {patient_info['name']}, 年龄: {patient_info['age']}岁, BMI: {patient_info['bmi']}\n\n"
            
            if diabetes_assessments:
                latest = diabetes_assessments[0]
                report += f"最新评估({latest['assessment_date']}):\n"
                report += f"- 空腹血糖: {latest.get('fasting_glucose', 'N/A')} mmol/L\n"
                report += f"- 餐后血糖: {latest.get('postprandial_glucose', 'N/A')} mmol/L\n"
                report += f"- HbA1c: {latest.get('hba1c', 'N/A')}%\n"
                report += f"- 控制状态: {latest.get('control_status', 'N/A')}\n"
            
            # 异常检验结果
            abnormal_results = [r for r in lab_results if r.get('is_abnormal')]
            if abnormal_results:
                report += f"\n异常检验结果({len(abnormal_results)}项):\n"
                for result in abnormal_results[:5]:
                    report += f"- {result['test_item']}: {result['result_value']} {result.get('unit', '')} (参考范围: {result.get('reference_range', 'N/A')})\n"
            
            return report
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return f"评估失败: {str(e)}"
    
    def check_medication_safety(self, patient_id: str, new_medication: str) -> str:
        """
        检查用药安全性
        
        Args:
            patient_id: 患者ID
            new_medication: 新药物名称
            
        Returns:
            安全检查结果
        """
        logger.info(f"检查用药安全: 患者{patient_id}, 药物{new_medication}")
        
        try:
            # 获取当前用药
            current_meds = self.medical_retriever.get_patient_medications(patient_id, limit=10)
            
            med_info = {
                "new_medication": new_medication,
                "current_medications": [m['drug_name'] for m in current_meds]
            }
            
            # 执行安全检查
            safety_result = self.safety_checker.check_medication_safety(med_info)
            
            report = f"用药安全检查结果:\n"
            report += f"- 安全性: {'安全' if safety_result['safe'] else '需要注意'}\n"
            
            if safety_result['warnings']:
                report += f"- 警告:\n"
                for warning in safety_result['warnings']:
                    report += f"  * {warning}\n"
            
            report += f"\n当前用药({len(current_meds)}种):\n"
            for med in current_meds[:5]:
                report += f"- {med['drug_name']} ({med.get('dosage', 'N/A')})\n"
            
            return report
        except Exception as e:
            logger.error(f"安全检查失败: {e}")
            return f"检查失败: {str(e)}"


def create_medical_tools(query_engine: Optional[QueryEngine] = None) -> MedicalTools:
    """
    创建医疗工具集
    
    Args:
        query_engine: RAG查询引擎
        
    Returns:
        MedicalTools对象
    """
    return MedicalTools(query_engine)


if __name__ == "__main__":
    # 测试工具集
    tools = create_medical_tools()
    
    test_patient_id = "1001_0_20210730"
    
    logger.info(f"测试患者ID: {test_patient_id}")
    
    # 测试获取患者信息
    print("\n" + "="*80)
    print("患者信息:")
    print("="*80)
    print(tools.get_patient_information(test_patient_id))
    
    # 测试糖尿病风险评估
    print("\n" + "="*80)
    print("糖尿病风险评估:")
    print("="*80)
    print(tools.assess_diabetes_risk(test_patient_id))
