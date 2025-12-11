"""
医疗数据检索模块
提供患者信息、病历、检验结果等医疗数据的查询功能
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from src.database.mysql_connector import get_db_connector
from src.utils.logger import logger


class MedicalDataRetriever:
    """医疗数据检索器"""
    
    def __init__(self):
        self.db = get_db_connector()
    
    def get_patient_info(self, patient_id: str) -> Optional[Dict]:
        """
        获取患者基本信息
        
        Args:
            patient_id: 患者ID
            
        Returns:
            患者信息字典,如果不存在返回None
        """
        query = """
        SELECT * FROM patient_info 
        WHERE patient_id = :patient_id
        """
        results = self.db.execute_query(query, {"patient_id": patient_id})
        return results[0] if results else None
    
    def get_patient_medical_records(self, patient_id: str, limit: int = 10) -> List[Dict]:
        """
        获取患者病历记录
        
        Args:
            patient_id: 患者ID
            limit: 返回记录数限制
            
        Returns:
            病历记录列表
        """
        query = """
        SELECT * FROM medical_records 
        WHERE patient_id = :patient_id 
        ORDER BY visit_date DESC 
        LIMIT :limit
        """
        return self.db.execute_query(query, {"patient_id": patient_id, "limit": limit})
    
    def get_patient_lab_results(self, patient_id: str, test_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        获取患者检验结果
        
        Args:
            patient_id: 患者ID
            test_type: 检验类型(可选)
            limit: 返回记录数限制
            
        Returns:
            检验结果列表
        """
        if test_type:
            query = """
            SELECT * FROM lab_results 
            WHERE patient_id = :patient_id AND test_type = :test_type
            ORDER BY test_date DESC 
            LIMIT :limit
            """
            params = {"patient_id": patient_id, "test_type": test_type, "limit": limit}
        else:
            query = """
            SELECT * FROM lab_results 
            WHERE patient_id = :patient_id 
            ORDER BY test_date DESC 
            LIMIT :limit
            """
            params = {"patient_id": patient_id, "limit": limit}
        
        return self.db.execute_query(query, params)
    
    def get_patient_medications(self, patient_id: str, limit: int = 10) -> List[Dict]:
        """
        获取患者用药记录
        
        Args:
            patient_id: 患者ID
            limit: 返回记录数限制
            
        Returns:
            用药记录列表
        """
        query = """
        SELECT * FROM medication_records 
        WHERE patient_id = :patient_id 
        ORDER BY medication_date DESC 
        LIMIT :limit
        """
        return self.db.execute_query(query, {"patient_id": patient_id, "limit": limit})
    
    def get_patient_diagnoses(self, patient_id: str, limit: int = 10) -> List[Dict]:
        """
        获取患者诊断记录
        
        Args:
            patient_id: 患者ID
            limit: 返回记录数限制
            
        Returns:
            诊断记录列表
        """
        query = """
        SELECT * FROM diagnosis_records 
        WHERE patient_id = :patient_id 
        ORDER BY diagnosis_date DESC 
        LIMIT :limit
        """
        return self.db.execute_query(query, {"patient_id": patient_id, "limit": limit})
    
    def get_diabetes_assessment(self, patient_id: str, limit: int = 5) -> List[Dict]:
        """
        获取糖尿病控制评估记录
        
        Args:
            patient_id: 患者ID
            limit: 返回记录数限制
            
        Returns:
            糖尿病评估记录列表
        """
        query = """
        SELECT * FROM diabetes_control_assessment 
        WHERE patient_id = :patient_id 
        ORDER BY assessment_date DESC 
        LIMIT :limit
        """
        return self.db.execute_query(query, {"patient_id": patient_id, "limit": limit})
    
    def get_hypertension_assessment(self, patient_id: str, limit: int = 5) -> List[Dict]:
        """
        获取高血压风险评估记录
        
        Args:
            patient_id: 患者ID
            limit: 返回记录数限制
            
        Returns:
            高血压评估记录列表
        """
        query = """
        SELECT * FROM hypertension_risk_assessment 
        WHERE patient_id = :patient_id 
        ORDER BY assessment_date DESC 
        LIMIT :limit
        """
        return self.db.execute_query(query, {"patient_id": patient_id, "limit": limit})
    
    def get_patient_comprehensive_data(self, patient_id: str) -> Dict[str, Any]:
        """
        获取患者综合数据(包含所有相关信息)
        
        Args:
            patient_id: 患者ID
            
        Returns:
            包含患者所有信息的字典
        """
        logger.info(f"获取患者综合数据: {patient_id}")
        
        data = {
            "patient_info": self.get_patient_info(patient_id),
            "medical_records": self.get_patient_medical_records(patient_id, limit=5),
            "lab_results": self.get_patient_lab_results(patient_id, limit=10),
            "medications": self.get_patient_medications(patient_id, limit=10),
            "diagnoses": self.get_patient_diagnoses(patient_id, limit=5),
            "diabetes_assessment": self.get_diabetes_assessment(patient_id, limit=3),
            "hypertension_assessment": self.get_hypertension_assessment(patient_id, limit=3)
        }
        
        return data
    
    def search_guideline_recommendations(
        self, 
        disease_type: Optional[str] = None,
        recommendation_level: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索指南推荐
        
        Args:
            disease_type: 疾病类型(高血压/糖尿病/冠心病/脑卒中)
            recommendation_level: 推荐等级(ⅠA/ⅠB/ⅡA/ⅡB/Ⅲ)
            limit: 返回记录数限制
            
        Returns:
            指南推荐列表
        """
        conditions = ["is_active = 1"]
        params = {"limit": limit}
        
        if disease_type:
            conditions.append("disease_type = :disease_type")
            params["disease_type"] = disease_type
        
        if recommendation_level:
            conditions.append("recommendation_level = :recommendation_level")
            params["recommendation_level"] = recommendation_level
        
        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT * FROM guideline_recommendations 
        WHERE {where_clause}
        ORDER BY update_date DESC 
        LIMIT :limit
        """
        
        return self.db.execute_query(query, params)
    
    def get_abnormal_lab_results(self, patient_id: str, limit: int = 10) -> List[Dict]:
        """
        获取患者异常检验结果
        
        Args:
            patient_id: 患者ID
            limit: 返回记录数限制
            
        Returns:
            异常检验结果列表
        """
        query = """
        SELECT * FROM lab_results 
        WHERE patient_id = :patient_id AND is_abnormal = 1
        ORDER BY test_date DESC 
        LIMIT :limit
        """
        return self.db.execute_query(query, {"patient_id": patient_id, "limit": limit})


# 全局医疗数据检索器实例
medical_retriever = MedicalDataRetriever()


def get_medical_retriever() -> MedicalDataRetriever:
    """获取医疗数据检索器实例"""
    return medical_retriever


if __name__ == "__main__":
    # 测试医疗数据检索
    retriever = get_medical_retriever()
    
    # 测试患者ID
    test_patient_id = "1001_0_20210730"
    
    logger.info(f"测试患者ID: {test_patient_id}")
    
    # 获取患者信息
    patient_info = retriever.get_patient_info(test_patient_id)
    if patient_info:
        logger.success(f"✅ 患者信息: {patient_info['name']}, 年龄: {patient_info['age']}, BMI: {patient_info['bmi']}")
    
    # 获取综合数据
    comprehensive_data = retriever.get_patient_comprehensive_data(test_patient_id)
    logger.info(f"病历记录数: {len(comprehensive_data['medical_records'])}")
    logger.info(f"检验结果数: {len(comprehensive_data['lab_results'])}")
    logger.info(f"用药记录数: {len(comprehensive_data['medications'])}")
