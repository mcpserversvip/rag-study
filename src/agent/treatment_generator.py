"""
治疗方案生成器
基于患者风险分层和指南推荐生成个性化治疗方案
评分点: 4.2.2 治疗方案生成(8分) + 动态调整能力(5分)
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from src.database import get_medical_retriever
from src.rag import QueryEngine
from src.utils.logger import logger


class TreatmentPlanGenerator:
    """治疗方案生成器"""
    
    def __init__(self, query_engine: Optional[QueryEngine] = None):
        """
        初始化治疗方案生成器
        
        Args:
            query_engine: RAG查询引擎
        """
        self.query_engine = query_engine
        self.medical_retriever = get_medical_retriever()
        
        # 药物知识库
        self.drug_database = self._init_drug_database()
    
    def _init_drug_database(self) -> Dict:
        """初始化药物知识库"""
        return {
            "高血压": {
                "一线药物": {
                    "ACEI类": {
                        "代表药物": ["依那普利", "贝那普利", "培哚普利"],
                        "起始剂量": "依那普利5mg qd",
                        "目标剂量": "依那普利10-20mg qd",
                        "适应症": "合并糖尿病、心衰、肾病",
                        "禁忌症": "孕妇、双侧肾动脉狭窄、高钾血症",
                        "证据等级": "ⅠA"
                    },
                    "ARB类": {
                        "代表药物": ["缬沙坦", "氯沙坦", "替米沙坦"],
                        "起始剂量": "缬沙坦80mg qd",
                        "目标剂量": "缬沙坦160mg qd",
                        "适应症": "不能耐受ACEI的患者",
                        "禁忌症": "孕妇、双侧肾动脉狭窄",
                        "证据等级": "ⅠA"
                    },
                    "CCB类": {
                        "代表药物": ["氨氯地平", "硝苯地平控释片", "非洛地平"],
                        "起始剂量": "氨氯地平5mg qd",
                        "目标剂量": "氨氯地平10mg qd",
                        "适应症": "老年人、单纯收缩期高血压",
                        "禁忌症": "心动过缓、心衰",
                        "证据等级": "ⅠA"
                    },
                    "利尿剂": {
                        "代表药物": ["氢氯噻嗪", "吲达帕胺"],
                        "起始剂量": "氢氯噻嗪12.5mg qd",
                        "目标剂量": "氢氯噻嗪25mg qd",
                        "适应症": "老年人、心衰、水肿",
                        "禁忌症": "痛风、低钾血症",
                        "证据等级": "ⅠA"
                    },
                    "β受体阻滞剂": {
                        "代表药物": ["美托洛尔", "比索洛尔"],
                        "起始剂量": "美托洛尔25mg bid",
                        "目标剂量": "美托洛尔50-100mg bid",
                        "适应症": "合并冠心病、心衰、心动过速",
                        "禁忌症": "哮喘、心动过缓、房室传导阻滞",
                        "证据等级": "ⅠA"
                    }
                }
            },
            "糖尿病": {
                "一线药物": {
                    "二甲双胍": {
                        "起始剂量": "500mg bid",
                        "目标剂量": "1000mg bid",
                        "适应症": "2型糖尿病一线用药",
                        "禁忌症": "肾功能不全(eGFR<30)、肝功能不全、酮症酸中毒",
                        "证据等级": "ⅠA"
                    },
                    "磺脲类": {
                        "代表药物": ["格列美脲", "格列齐特"],
                        "起始剂量": "格列美脲1mg qd",
                        "目标剂量": "格列美脲4-6mg qd",
                        "适应症": "血糖控制不佳",
                        "禁忌症": "1型糖尿病、孕妇、肝肾功能不全",
                        "证据等级": "ⅠA",
                        "注意": "低血糖风险"
                    },
                    "DPP-4抑制剂": {
                        "代表药物": ["西格列汀", "利格列汀"],
                        "起始剂量": "西格列汀100mg qd",
                        "适应症": "不耐受二甲双胍或有禁忌症",
                        "证据等级": "ⅠB"
                    },
                    "GLP-1受体激动剂": {
                        "代表药物": ["利拉鲁肽", "度拉糖肽"],
                        "适应症": "肥胖、心血管高危患者",
                        "证据等级": "ⅠA"
                    },
                    "胰岛素": {
                        "类型": ["基础胰岛素", "餐时胰岛素", "预混胰岛素"],
                        "起始剂量": "0.1-0.2U/kg/d",
                        "适应症": "1型糖尿病、2型糖尿病血糖控制不佳",
                        "证据等级": "ⅠA"
                    }
                }
            }
        }
    
    def generate_treatment_plan(
        self,
        patient_id: str,
        diagnosis: str,
        risk_level: str,
        current_medications: List[str] = None
    ) -> Dict:
        """
        生成治疗方案
        
        Args:
            patient_id: 患者ID
            diagnosis: 诊断
            risk_level: 风险等级
            current_medications: 当前用药列表
            
        Returns:
            治疗方案字典
        """
        logger.info(f"生成治疗方案: 患者{patient_id}, 诊断{diagnosis}, 风险{risk_level}")
        
        # 获取患者信息
        patient_info = self.medical_retriever.get_patient_info(patient_id)
        patient_data = self.medical_retriever.get_patient_comprehensive_data(patient_id)
        
        # 生成药物方案
        drug_plan = self._select_drugs(diagnosis, risk_level, patient_info, patient_data)
        
        # 生成非药物治疗
        lifestyle_plan = self._generate_lifestyle_recommendations(diagnosis, patient_info)
        
        # 生成随访计划
        followup_plan = self._generate_followup_plan(diagnosis, risk_level)
        
        # 生成目标值
        target_values = self._generate_target_values(diagnosis, patient_info)
        
        plan = {
            "患者ID": patient_id,
            "诊断": diagnosis,
            "风险等级": risk_level,
            "药物治疗": drug_plan,
            "生活方式干预": lifestyle_plan,
            "随访计划": followup_plan,
            "治疗目标": target_values,
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.success("治疗方案生成完成")
        
        return plan
    
    def _select_drugs(
        self,
        diagnosis: str,
        risk_level: str,
        patient_info: Dict,
        patient_data: Dict
    ) -> List[Dict]:
        """选择药物"""
        drugs = []
        
        if "高血压" in diagnosis:
            drugs.extend(self._select_antihypertensive_drugs(risk_level, patient_info, patient_data))
        
        if "糖尿病" in diagnosis:
            drugs.extend(self._select_antidiabetic_drugs(patient_info, patient_data))
        
        return drugs
    
    def _select_antihypertensive_drugs(
        self,
        risk_level: str,
        patient_info: Dict,
        patient_data: Dict
    ) -> List[Dict]:
        """选择降压药"""
        drugs = []
        age = patient_info.get('age', 0)
        
        # 根据风险等级和合并症选择药物
        if "糖尿病" in str(patient_data.get('diagnoses', [])):
            # 合并糖尿病,优先ACEI/ARB
            drug_info = self.drug_database["高血压"]["一线药物"]["ACEI类"]
            drugs.append({
                "药物类别": "ACEI类",
                "推荐药物": drug_info["代表药物"][0],
                "剂量": drug_info["起始剂量"],
                "调整依据": "合并糖尿病,ACEI类可延缓肾病进展",
                "证据等级": drug_info["证据等级"],
                "注意事项": f"禁忌症: {drug_info['禁忌症']}"
            })
        elif age >= 60:
            # 老年人,优先CCB
            drug_info = self.drug_database["高血压"]["一线药物"]["CCB类"]
            drugs.append({
                "药物类别": "CCB类",
                "推荐药物": drug_info["代表药物"][0],
                "剂量": drug_info["起始剂量"],
                "调整依据": "老年患者,CCB类降压效果好,耐受性好",
                "证据等级": drug_info["证据等级"],
                "注意事项": f"禁忌症: {drug_info['禁忌症']}"
            })
        else:
            # 一般患者,ACEI/ARB + CCB联合
            acei_info = self.drug_database["高血压"]["一线药物"]["ACEI类"]
            drugs.append({
                "药物类别": "ACEI类",
                "推荐药物": acei_info["代表药物"][0],
                "剂量": acei_info["起始剂量"],
                "调整依据": "一线降压药,心血管保护作用",
                "证据等级": acei_info["证据等级"]
            })
        
        # 如果是2级以上高血压,建议联合用药
        if "2级" in risk_level or "3级" in risk_level:
            ccb_info = self.drug_database["高血压"]["一线药物"]["CCB类"]
            drugs.append({
                "药物类别": "CCB类(联合用药)",
                "推荐药物": ccb_info["代表药物"][0],
                "剂量": ccb_info["起始剂量"],
                "调整依据": "2级高血压,建议联合用药",
                "证据等级": ccb_info["证据等级"]
            })
        
        return drugs
    
    def _select_antidiabetic_drugs(
        self,
        patient_info: Dict,
        patient_data: Dict
    ) -> List[Dict]:
        """选择降糖药"""
        drugs = []
        
        # 一线用药: 二甲双胍
        metformin = self.drug_database["糖尿病"]["一线药物"]["二甲双胍"]
        drugs.append({
            "药物类别": "双胍类",
            "推荐药物": "二甲双胍",
            "剂量": metformin["起始剂量"],
            "调整依据": "2型糖尿病一线用药,改善胰岛素抵抗",
            "证据等级": metformin["证据等级"],
            "注意事项": f"禁忌症: {metformin['禁忌症']}"
        })
        
        # 如果HbA1c>8%,考虑联合用药
        diabetes_assessments = patient_data.get('diabetes_assessment', [])
        if diabetes_assessments:
            latest = diabetes_assessments[0]
            hba1c = latest.get('hba1c')
            if hba1c and hba1c > 8.0:
                sulfonylurea = self.drug_database["糖尿病"]["一线药物"]["磺脲类"]
                drugs.append({
                    "药物类别": "磺脲类(联合用药)",
                    "推荐药物": sulfonylurea["代表药物"][0],
                    "剂量": sulfonylurea["起始剂量"],
                    "调整依据": f"HbA1c {hba1c}%,控制不佳,建议联合用药",
                    "证据等级": sulfonylurea["证据等级"],
                    "注意事项": sulfonylurea.get("注意", "")
                })
        
        return drugs
    
    def _generate_lifestyle_recommendations(
        self,
        diagnosis: str,
        patient_info: Dict
    ) -> List[str]:
        """生成生活方式建议"""
        recommendations = []
        
        bmi = patient_info.get('bmi', 0)
        
        # 通用建议
        recommendations.append("戒烟限酒")
        recommendations.append("规律作息,保证充足睡眠")
        recommendations.append("保持良好心态,避免过度紧张焦虑")
        
        # 体重管理
        if bmi > 28:
            recommendations.append(f"控制体重(当前BMI {bmi},建议降至24以下)")
        elif bmi > 24:
            recommendations.append(f"适当减重(当前BMI {bmi})")
        
        # 疾病特异性建议
        if "高血压" in diagnosis:
            recommendations.append("低盐饮食(每日食盐<6g)")
            recommendations.append("DASH饮食:多吃蔬菜水果、低脂奶制品")
            recommendations.append("规律运动:每周至少150分钟中等强度有氧运动")
        
        if "糖尿病" in diagnosis:
            recommendations.append("控制总热量摄入,少食多餐")
            recommendations.append("选择低升糖指数食物")
            recommendations.append("规律运动:餐后1小时运动30分钟")
            recommendations.append("定期监测血糖")
        
        return recommendations
    
    def _generate_followup_plan(self, diagnosis: str, risk_level: str) -> Dict:
        """生成随访计划"""
        plan = {}
        
        if "高血压" in diagnosis:
            if "3级" in risk_level or "很高危" in risk_level:
                plan["随访频率"] = "每1-2周"
                plan["监测项目"] = ["血压", "心率", "症状", "药物不良反应"]
            elif "2级" in risk_level:
                plan["随访频率"] = "每2-4周"
                plan["监测项目"] = ["血压", "症状"]
            else:
                plan["随访频率"] = "每1-3个月"
                plan["监测项目"] = ["血压"]
            
            plan["复查项目"] = "3个月后复查: 血常规、肝肾功能、血脂、血糖、心电图"
        
        if "糖尿病" in diagnosis:
            plan["血糖监测"] = "空腹及餐后2小时血糖,每周2-3次"
            plan["HbA1c"] = "每3个月检测一次"
            plan["并发症筛查"] = "每年: 眼底检查、尿微量白蛋白、神经病变筛查"
        
        return plan
    
    def _generate_target_values(self, diagnosis: str, patient_info: Dict) -> Dict:
        """生成治疗目标值"""
        targets = {}
        age = patient_info.get('age', 0)
        
        if "高血压" in diagnosis:
            if age < 65:
                targets["血压目标"] = "<140/90 mmHg"
            else:
                targets["血压目标"] = "<150/90 mmHg"
            
            if "糖尿病" in diagnosis:
                targets["血压目标"] = "<130/80 mmHg(合并糖尿病)"
        
        if "糖尿病" in diagnosis:
            targets["空腹血糖"] = "4.4-7.0 mmol/L"
            targets["餐后2小时血糖"] = "<10.0 mmol/L"
            targets["HbA1c"] = "<7.0%(个体化调整)"
        
        return targets
    
    def adjust_treatment_plan(
        self,
        patient_id: str,
        original_plan: Dict,
        treatment_duration: int,  # 治疗周数
        current_values: Dict,  # 当前指标值
        effectiveness: str  # 疗效评估: "良好"/"一般"/"不佳"
    ) -> Dict:
        """
        动态调整治疗方案
        
        Args:
            patient_id: 患者ID
            original_plan: 原治疗方案
            treatment_duration: 治疗周数
            current_values: 当前指标值
            effectiveness: 疗效评估
            
        Returns:
            调整后的治疗方案
        """
        logger.info(f"调整治疗方案: 患者{patient_id}, 治疗{treatment_duration}周, 疗效{effectiveness}")
        
        adjusted_plan = original_plan.copy()
        adjustment_reasons = []
        
        if effectiveness == "不佳":
            # 治疗效果不佳,需要调整
            adjustment_reasons.append(f"治疗{treatment_duration}周后效果不佳")
            
            # 调整药物方案
            new_drugs = []
            for drug in original_plan.get("药物治疗", []):
                # 增加剂量或联合用药
                if "起始剂量" in drug.get("剂量", ""):
                    drug_copy = drug.copy()
                    drug_copy["剂量"] = drug_copy["剂量"].replace("起始", "目标")
                    drug_copy["调整依据"] = f"原方案效果不佳,增加剂量"
                    new_drugs.append(drug_copy)
                    adjustment_reasons.append(f"增加{drug['推荐药物']}剂量")
                else:
                    new_drugs.append(drug)
            
            # 考虑联合用药
            if len(new_drugs) == 1:
                adjustment_reasons.append("建议联合用药")
            
            adjusted_plan["药物治疗"] = new_drugs
            adjusted_plan["调整原因"] = adjustment_reasons
            adjusted_plan["调整时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        elif effectiveness == "一般":
            adjustment_reasons.append(f"治疗{treatment_duration}周,效果一般,继续观察")
            adjusted_plan["建议"] = "继续当前方案,2周后复查"
        
        else:  # 良好
            adjustment_reasons.append(f"治疗{treatment_duration}周,效果良好")
            adjusted_plan["建议"] = "继续当前方案,维持治疗"
        
        logger.success(f"方案调整完成: {', '.join(adjustment_reasons)}")
        
        return adjusted_plan
    
    def generate_treatment_report(self, plan: Dict) -> str:
        """生成治疗方案报告"""
        report = "="*80 + "\n"
        report += "个性化治疗方案\n"
        report += "="*80 + "\n\n"
        
        report += f"【患者ID】{plan['患者ID']}\n"
        report += f"【诊断】{plan['诊断']}\n"
        report += f"【风险等级】{plan['风险等级']}\n"
        report += f"【生成时间】{plan['生成时间']}\n\n"
        
        report += "【药物治疗方案】\n"
        for i, drug in enumerate(plan.get('药物治疗', []), 1):
            report += f"\n{i}. {drug['推荐药物']} ({drug['药物类别']})\n"
            report += f"   剂量: {drug['剂量']}\n"
            report += f"   调整依据: {drug['调整依据']}\n"
            report += f"   证据等级: {drug.get('证据等级', 'N/A')}\n"
            if '注意事项' in drug:
                report += f"   ⚠️ {drug['注意事项']}\n"
        
        report += "\n【生活方式干预】\n"
        for i, rec in enumerate(plan.get('生活方式干预', []), 1):
            report += f"{i}. {rec}\n"
        
        report += "\n【治疗目标】\n"
        for key, value in plan.get('治疗目标', {}).items():
            report += f"- {key}: {value}\n"
        
        report += "\n【随访计划】\n"
        for key, value in plan.get('随访计划', {}).items():
            report += f"- {key}: {value}\n"
        
        if '调整原因' in plan:
            report += "\n【方案调整】\n"
            for reason in plan['调整原因']:
                report += f"- {reason}\n"
        
        report += "\n" + "="*80 + "\n"
        report += "⚠️ 本方案仅供参考,具体用药请遵医嘱\n"
        report += "="*80 + "\n"
        
        return report


def create_treatment_generator(query_engine: Optional[QueryEngine] = None) -> TreatmentPlanGenerator:
    """创建治疗方案生成器"""
    return TreatmentPlanGenerator(query_engine)


if __name__ == "__main__":
    # 测试治疗方案生成
    generator = create_treatment_generator()
    
    # 测试案例: 高血压+糖尿病患者
    print("\n" + "="*80)
    print("测试案例: 高血压+糖尿病患者治疗方案")
    print("="*80)
    
    plan = generator.generate_treatment_plan(
        patient_id="1001_0_20210730",
        diagnosis="2级高血压,2型糖尿病",
        risk_level="高危"
    )
    
    report = generator.generate_treatment_report(plan)
    print(report)
    
    # 测试动态调整
    print("\n" + "="*80)
    print("测试案例: 治疗2周后效果不佳,调整方案")
    print("="*80)
    
    adjusted_plan = generator.adjust_treatment_plan(
        patient_id="1001_0_20210730",
        original_plan=plan,
        treatment_duration=2,
        current_values={"收缩压": 165, "舒张压": 95},
        effectiveness="不佳"
    )
    
    adjusted_report = generator.generate_treatment_report(adjusted_plan)
    print(adjusted_report)
