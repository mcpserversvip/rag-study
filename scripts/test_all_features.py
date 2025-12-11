"""
综合测试脚本
测试所有核心功能模块,对照评分标准验证
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import logger
from src.utils.term_mapper import get_term_mapper
from src.agent.diagnosis_engine import create_diagnosis_engine
from src.agent.treatment_generator import create_treatment_generator
from src.agent.evidence_system import EvidenceBasedRecommendation


def test_term_mapping():
    """测试术语标准化映射(4.1.1, 3分)"""
    logger.info("\n" + "="*80)
    logger.info("测试1: 术语标准化映射")
    logger.info("="*80)
    
    mapper = get_term_mapper()
    
    # 测试案例: "心梗"→"心肌梗死"
    test_term = "心梗"
    standard_term = mapper.normalize(test_term)
    
    print(f"\n输入术语: {test_term}")
    print(f"标准术语: {standard_term}")
    print(f"所有同义词: {', '.join(mapper.get_synonyms(test_term))}")
    
    assert standard_term == "心肌梗死", "术语映射失败"
    logger.success("✅ 术语标准化映射测试通过")
    
    return True


def test_diagnosis_engine():
    """测试诊断推理引擎(4.2.2, 7分)"""
    logger.info("\n" + "="*80)
    logger.info("测试2: 诊断推理能力")
    logger.info("="*80)
    
    engine = create_diagnosis_engine()
    
    # 测试案例: 高血压+糖尿病
    symptoms = ["头晕", "头痛", "多饮", "多尿"]
    lab_results = {
        "收缩压": 168,
        "舒张压": 98,
        "空腹血糖": 8.5,
        "HbA1c": 8.2
    }
    
    diagnoses = engine.differential_diagnosis(symptoms, lab_results)
    
    print(f"\n症状: {', '.join(symptoms)}")
    print(f"检验结果: {lab_results}")
    print(f"\n鉴别诊断结果(共{len(diagnoses)}个):")
    
    for i, diag in enumerate(diagnoses, 1):
        print(f"\n{i}. {diag['疾病']} - 概率: {diag['概率']}")
        print(f"   证据: {', '.join(diag['证据'][:2])}")
    
    assert len(diagnoses) >= 2, "诊断数量不足"
    assert diagnoses[0]['概率值'] > diagnoses[1]['概率值'], "概率排序错误"
    
    logger.success("✅ 诊断推理引擎测试通过")
    
    return True


def test_treatment_generator():
    """测试治疗方案生成器(4.2.2, 8分)"""
    logger.info("\n" + "="*80)
    logger.info("测试3: 治疗方案生成")
    logger.info("="*80)
    
    generator = create_treatment_generator()
    
    # 测试案例: 生成治疗方案
    plan = generator.generate_treatment_plan(
        patient_id="1001_0_20210730",
        diagnosis="2级高血压,2型糖尿病",
        risk_level="高危"
    )
    
    print(f"\n诊断: {plan['诊断']}")
    print(f"风险等级: {plan['风险等级']}")
    print(f"\n药物治疗方案({len(plan['药物治疗'])}种药物):")
    
    for drug in plan['药物治疗']:
        print(f"- {drug['推荐药物']}: {drug['剂量']}")
        print(f"  证据等级: {drug.get('证据等级', 'N/A')}")
    
    assert len(plan['药物治疗']) > 0, "未生成药物方案"
    assert '证据等级' in plan['药物治疗'][0], "缺少证据等级"
    
    logger.success("✅ 治疗方案生成器测试通过")
    
    return True


def test_dynamic_adjustment():
    """测试动态调整能力(4.2.2, 5分)"""
    logger.info("\n" + "="*80)
    logger.info("测试4: 动态调整能力")
    logger.info("="*80)
    
    generator = create_treatment_generator()
    
    # 原始方案
    original_plan = generator.generate_treatment_plan(
        patient_id="1001_0_20210730",
        diagnosis="2级高血压",
        risk_level="中危"
    )
    
    # 模拟治疗2周后效果不佳
    adjusted_plan = generator.adjust_treatment_plan(
        patient_id="1001_0_20210730",
        original_plan=original_plan,
        treatment_duration=2,
        current_values={"收缩压": 165, "舒张压": 95},
        effectiveness="不佳"
    )
    
    print(f"\n原方案药物数: {len(original_plan['药物治疗'])}")
    print(f"调整后药物数: {len(adjusted_plan['药物治疗'])}")
    print(f"调整原因: {', '.join(adjusted_plan.get('调整原因', []))}")
    
    assert '调整原因' in adjusted_plan, "缺少调整原因"
    assert len(adjusted_plan.get('调整原因', [])) > 0, "调整原因为空"
    
    logger.success("✅ 动态调整能力测试通过")
    
    return True


def test_evidence_annotation():
    """测试证据等级标注(4.2.3, 5分)"""
    logger.info("\n" + "="*80)
    logger.info("测试5: 证据等级标注")
    logger.info("="*80)
    
    ebr = EvidenceBasedRecommendation()
    
    recommendation = ebr.create_recommendation(
        content="建议使用ACEI类药物(如依那普利10mg qd)降压治疗",
        guideline="2023年中国高血压防治指南",
        pdf_page="第45页",
        mysql_table="patient_info",
        mysql_record="patient_id=1001_0_20210730"
    )
    
    print(f"\n推荐内容: {recommendation['内容']}")
    print(f"证据等级: {recommendation['证据等级']}")
    print(f"指南来源: {recommendation['指南来源']}")
    print(f"数据来源: PDF={recommendation['数据来源统计']['PDF']}, MySQL={recommendation['数据来源统计']['MySQL']}")
    
    assert '证据等级' in recommendation, "缺少证据等级"
    assert recommendation['证据等级'] in ['ⅠA', 'ⅠB', 'ⅡA', 'ⅡB', 'Ⅲ'], "证据等级格式错误"
    
    logger.success("✅ 证据等级标注测试通过")
    
    return True


def test_decision_tracing():
    """测试决策溯源(4.3.3, 3分)"""
    logger.info("\n" + "="*80)
    logger.info("测试6: 决策溯源")
    logger.info("="*80)
    
    ebr = EvidenceBasedRecommendation()
    
    recommendation = ebr.create_recommendation(
        content="联合降压方案",
        guideline="2023年中国高血压防治指南",
        pdf_page="第50页",
        mysql_table="medical_records",
        mysql_record="record_id=123",
        excel_file="糖尿病病例统计.xlsx",
        excel_row="第10行"
    )
    
    trace_report = recommendation['溯源信息']
    
    print(trace_report)
    
    assert 'PDF' in trace_report, "缺少PDF溯源"
    assert 'MySQL' in trace_report, "缺少MySQL溯源"
    assert 'Excel' in trace_report, "缺少Excel溯源"
    
    logger.success("✅ 决策溯源测试通过")
    
    return True


def run_all_tests():
    """运行所有测试"""
    logger.info("\n" + "="*80)
    logger.info("开始综合测试")
    logger.info("="*80)
    
    tests = [
        ("术语标准化映射", test_term_mapping, 3),
        ("诊断推理能力", test_diagnosis_engine, 7),
        ("治疗方案生成", test_treatment_generator, 8),
        ("动态调整能力", test_dynamic_adjustment, 5),
        ("证据等级标注", test_evidence_annotation, 5),
        ("决策溯源", test_decision_tracing, 3)
    ]
    
    passed = 0
    total_score = 0
    
    for name, test_func, score in tests:
        try:
            if test_func():
                passed += 1
                total_score += score
                logger.success(f"✅ {name} 测试通过 (+{score}分)")
        except Exception as e:
            logger.error(f"❌ {name} 测试失败: {e}")
    
    logger.info("\n" + "="*80)
    logger.info("测试总结")
    logger.info("="*80)
    logger.info(f"通过: {passed}/{len(tests)}")
    logger.info(f"累计得分: {total_score}分")
    logger.success("="*80)
    
    return total_score


if __name__ == "__main__":
    total_score = run_all_tests()
    
    print("\n" + "="*80)
    print(f"✅ 综合测试完成,累计得分: {total_score}分")
    print("="*80)
