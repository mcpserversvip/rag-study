"""
医疗安全检查模块
包含用药安全、伦理检查、人文关怀等功能
"""
from typing import Dict, List, Optional
import re

from src.utils.logger import logger
from src.config import settings


class SafetyChecker:
    """医疗安全检查器"""
    
    def __init__(self):
        """初始化安全检查器"""
        self.enable_safety_check = settings.enable_safety_check
        self.enable_ethics_check = settings.enable_ethics_check
        self.enable_humanistic_care = settings.enable_humanistic_care
        
        # 高风险关键词
        self.high_risk_keywords = [
            "立即", "紧急", "危险", "严重", "致命",
            "停药", "加量", "减量", "换药",
            "手术", "住院", "急诊"
        ]
        
        # 禁忌词
        self.forbidden_keywords = [
            "保证治愈", "完全治愈", "根治",
            "绝对安全", "没有副作用",
            "最好的药", "唯一的选择"
        ]
        
        # 需要人文关怀的情况
        self.care_keywords = [
            "担心", "害怕", "焦虑", "紧张",
            "痛苦", "难受", "不舒服",
            "并发症", "恶化", "严重"
        ]
    
    def check_medication_safety(self, medication_info: Dict) -> Dict[str, any]:
        """
        检查用药安全
        
        Args:
            medication_info: 用药信息字典
            
        Returns:
            检查结果字典
        """
        if not self.enable_safety_check:
            return {"safe": True, "warnings": []}
        
        logger.info("执行用药安全检查")
        
        warnings = []
        
        # 检查剂量是否合理(示例)
        if "dosage" in medication_info:
            dosage = medication_info["dosage"]
            # 这里可以添加具体的剂量检查逻辑
            logger.debug(f"检查剂量: {dosage}")
        
        # 检查药物相互作用(示例)
        if "current_medications" in medication_info and "new_medication" in medication_info:
            # 这里可以添加药物相互作用检查逻辑
            logger.debug("检查药物相互作用")
        
        # 检查禁忌症(示例)
        if "contraindications" in medication_info:
            contraindications = medication_info["contraindications"]
            if contraindications:
                warnings.append(f"注意禁忌症: {contraindications}")
        
        return {
            "safe": len(warnings) == 0,
            "warnings": warnings
        }
    
    def check_content_ethics(self, content: str) -> Dict[str, any]:
        """
        检查内容伦理
        
        Args:
            content: 待检查内容
            
        Returns:
            检查结果字典
        """
        if not self.enable_ethics_check:
            return {"passed": True, "issues": []}
        
        logger.info("执行伦理检查")
        
        issues = []
        
        # 检查是否包含禁忌词
        for keyword in self.forbidden_keywords:
            if keyword in content:
                issues.append(f"包含不当承诺: '{keyword}'")
                logger.warning(f"发现禁忌词: {keyword}")
        
        # 检查是否过度承诺疗效
        if re.search(r'(100%|百分之百|一定|必然).*?(治愈|康复|痊愈)', content):
            issues.append("存在过度承诺疗效的表述")
        
        # 检查是否尊重患者自主权
        if "必须" in content and "建议" not in content:
            issues.append("表述过于强制,建议使用'建议'等词汇")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def detect_high_risk_content(self, content: str) -> Dict[str, any]:
        """
        检测高风险内容
        
        Args:
            content: 待检测内容
            
        Returns:
            检测结果字典
        """
        logger.info("检测高风险内容")
        
        high_risk_items = []
        
        for keyword in self.high_risk_keywords:
            if keyword in content:
                high_risk_items.append(keyword)
        
        is_high_risk = len(high_risk_items) > 0
        
        if is_high_risk:
            logger.warning(f"检测到高风险内容,关键词: {high_risk_items}")
        
        return {
            "is_high_risk": is_high_risk,
            "risk_keywords": high_risk_items,
            "warning_message": "⚠️ 本建议涉及重要医疗决策,请务必咨询主治医生后再执行。" if is_high_risk else ""
        }
    
    def add_humanistic_care(self, content: str, patient_context: Optional[str] = None) -> str:
        """
        添加人文关怀内容
        
        Args:
            content: 原始内容
            patient_context: 患者上下文(可选)
            
        Returns:
            添加人文关怀后的内容
        """
        if not self.enable_humanistic_care:
            return content
        
        logger.info("添加人文关怀内容")
        
        # 检查是否需要特别关怀
        needs_care = False
        if patient_context:
            for keyword in self.care_keywords:
                if keyword in patient_context:
                    needs_care = True
                    break
        
        # 添加人文关怀前缀
        care_prefix = ""
        if needs_care:
            care_prefix = "💙 我理解您的担忧和不安。请放心,我们会一起面对这个问题。\n\n"
        
        # 添加人文关怀后缀
        care_suffix = "\n\n💙 温馨提示:\n"
        care_suffix += "- 慢性病管理是一个长期过程,请保持耐心和信心\n"
        care_suffix += "- 规律服药、健康生活方式是控制疾病的关键\n"
        care_suffix += "- 如有任何不适或疑问,请及时咨询您的主治医生\n"
        care_suffix += "- 保持积极乐观的心态,对疾病控制很有帮助\n"
        
        return care_prefix + content + care_suffix
    
    def add_disclaimer(self, content: str) -> str:
        """
        添加免责声明
        
        Args:
            content: 原始内容
            
        Returns:
            添加免责声明后的内容
        """
        disclaimer = "\n\n" + "="*80 + "\n"
        disclaimer += "⚠️ 【重要声明】\n"
        disclaimer += "本建议仅供医疗专业人员参考,不能替代医生的临床判断。\n"
        disclaimer += "所有诊疗决策请在医生指导下进行。\n"
        disclaimer += "如有紧急情况,请立即就医或拨打120急救电话。\n"
        disclaimer += "="*80
        
        return content + disclaimer
    
    def comprehensive_check(
        self, 
        content: str, 
        patient_context: Optional[str] = None,
        medication_info: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        综合安全检查
        
        Args:
            content: 待检查内容
            patient_context: 患者上下文
            medication_info: 用药信息
            
        Returns:
            综合检查结果
        """
        logger.info("执行综合安全检查")
        
        results = {
            "original_content": content,
            "processed_content": content,
            "checks": {}
        }
        
        # 1. 伦理检查
        ethics_result = self.check_content_ethics(content)
        results["checks"]["ethics"] = ethics_result
        
        if not ethics_result["passed"]:
            logger.warning(f"伦理检查未通过: {ethics_result['issues']}")
        
        # 2. 高风险检测
        risk_result = self.detect_high_risk_content(content)
        results["checks"]["risk"] = risk_result
        
        # 3. 用药安全检查
        if medication_info:
            med_safety_result = self.check_medication_safety(medication_info)
            results["checks"]["medication_safety"] = med_safety_result
        
        # 4. 添加人文关怀
        processed_content = self.add_humanistic_care(content, patient_context)
        
        # 5. 添加高风险警告
        if risk_result["is_high_risk"]:
            processed_content = risk_result["warning_message"] + "\n\n" + processed_content
        
        # 6. 添加免责声明
        processed_content = self.add_disclaimer(processed_content)
        
        results["processed_content"] = processed_content
        results["safe_to_display"] = ethics_result["passed"]
        
        return results


# 全局安全检查器实例
safety_checker = SafetyChecker()


def get_safety_checker() -> SafetyChecker:
    """获取安全检查器实例"""
    return safety_checker


if __name__ == "__main__":
    # 测试安全检查
    checker = get_safety_checker()
    
    # 测试内容
    test_content = "建议您立即停药,改用新的降糖药物。这个方案保证治愈您的糖尿病。"
    test_context = "患者表示很担心并发症"
    
    logger.info("测试安全检查")
    
    result = checker.comprehensive_check(
        content=test_content,
        patient_context=test_context
    )
    
    print("\n" + "="*80)
    print("原始内容:")
    print(result["original_content"])
    print("\n" + "="*80)
    print("检查结果:")
    print(f"伦理检查: {'通过' if result['checks']['ethics']['passed'] else '未通过'}")
    if not result['checks']['ethics']['passed']:
        print(f"  问题: {result['checks']['ethics']['issues']}")
    print(f"高风险检测: {'是' if result['checks']['risk']['is_high_risk'] else '否'}")
    if result['checks']['risk']['is_high_risk']:
        print(f"  风险关键词: {result['checks']['risk']['risk_keywords']}")
    print("\n" + "="*80)
    print("处理后内容:")
    print(result["processed_content"])
    print("="*80)
