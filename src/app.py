"""
Flask Web应用主程序
提供医疗助手的Web API接口
"""
import sys
from pathlib import Path

# 添加项目根目录到路径，确保能正确导入 src 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS

from src.config import settings, init_environment
from src.utils.logger import logger
from src.rag import get_knowledge_builder, create_query_engine
from src.agent import get_safety_checker, create_medical_tools
from src.database import get_medical_retriever

# 初始化环境
init_environment()

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS

# 全局变量
query_engine = None
medical_tools = None
safety_checker = None
medical_retriever = None


def initialize_app():
    """初始化应用组件"""
    global query_engine, medical_tools, safety_checker, medical_retriever
    
    logger.info("初始化应用组件...")
    
    try:
        # 1. 加载知识库
        logger.info("加载RAG知识库...")
        builder = get_knowledge_builder()
        index = builder.load_index(settings.knowledge_base_path)
        
        if index:
            query_engine = create_query_engine(index)
            logger.success("RAG知识库加载成功")
        else:
            logger.warning("RAG知识库未找到,部分功能可能不可用")
        
        # 2. 初始化医疗工具
        medical_tools = create_medical_tools(query_engine)
        logger.success("医疗工具集初始化成功")
        
        # 3. 初始化安全检查器
        safety_checker = get_safety_checker()
        logger.success("安全检查器初始化成功")
        
        # 4. 初始化医疗数据检索器
        medical_retriever = get_medical_retriever()
        logger.success("医疗数据检索器初始化成功")
        
        logger.success("✅ 应用初始化完成")
        
    except Exception as e:
        logger.error(f"应用初始化失败: {e}")
        raise


@app.route('/', methods=['GET'])
def home():
    """首页"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "components": {
            "rag_engine": query_engine is not None,
            "medical_tools": medical_tools is not None,
            "safety_checker": safety_checker is not None,
            "database": medical_retriever is not None
        }
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    对话接口(流式响应)
    
    请求体:
    {
        "question": "问题内容",
        "patient_id": "患者ID(可选)",
        "enable_safety_check": true
    }
    """
    try:
        data = request.json
        question = data.get('question', '')
        patient_id = data.get('patient_id')
        enable_safety = data.get('enable_safety_check', True)
        
        if not question:
            return jsonify({"error": "问题不能为空"}), 400
        
        if not query_engine:
            return jsonify({"error": "RAG引擎未初始化,请先构建知识库"}), 500
        
        def generate():
            """生成流式响应"""
            try:
                # 如果提供了患者ID,添加患者上下文
                patient_context = None
                if patient_id:
                    patient_info = medical_retriever.get_patient_info(patient_id)
                    if patient_info:
                        patient_context = f"患者: {patient_info['name']}, 年龄: {patient_info['age']}岁, BMI: {patient_info['bmi']}"
                
                # 流式查询
                response_text = ""
                for chunk in query_engine.query_stream(question):
                    response_text += chunk
                    yield chunk
                
                # 如果启用安全检查,在最后添加安全提示
                if enable_safety and safety_checker:
                    # 检查高风险内容
                    risk_result = safety_checker.detect_high_risk_content(response_text)
                    if risk_result["is_high_risk"]:
                        yield "\n\n" + risk_result["warning_message"]
                    
                    # 添加免责声明
                    disclaimer = "\n\n" + "="*60 + "\n"
                    disclaimer += "⚠️ 本建议仅供参考,具体诊疗请咨询医生。\n"
                    disclaimer += "="*60
                    yield disclaimer
                    
            except Exception as e:
                logger.error(f"对话生成失败: {e}")
                yield f"\n\n错误: {str(e)}"
        
        return Response(generate(), mimetype="text/plain")
        
    except Exception as e:
        logger.error(f"对话接口错误: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/patient/<patient_id>', methods=['GET'])
def get_patient(patient_id: str):
    """
    获取患者信息接口
    
    参数:
        patient_id: 患者ID
    """
    try:
        if not medical_retriever:
            return jsonify({"error": "数据库未初始化"}), 500
        
        patient_info = medical_retriever.get_patient_info(patient_id)
        
        if patient_info:
            return jsonify(patient_info)
        else:
            return jsonify({"error": f"未找到患者: {patient_id}"}), 404
            
    except Exception as e:
        logger.error(f"获取患者信息失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/patient/<patient_id>/comprehensive', methods=['GET'])
def get_patient_comprehensive(patient_id: str):
    """
    获取患者综合数据接口
    
    参数:
        patient_id: 患者ID
    """
    try:
        if not medical_retriever:
            return jsonify({"error": "数据库未初始化"}), 500
        
        data = medical_retriever.get_patient_comprehensive_data(patient_id)
        
        if data.get('patient_info'):
            return jsonify(data)
        else:
            return jsonify({"error": f"未找到患者: {patient_id}"}), 404
            
    except Exception as e:
        logger.error(f"获取综合数据失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/assessment/diabetes/<patient_id>', methods=['GET'])
def assess_diabetes(patient_id: str):
    """
    糖尿病风险评估接口
    
    参数:
        patient_id: 患者ID
    """
    try:
        if not medical_tools:
            return jsonify({"error": "医疗工具未初始化"}), 500
        
        result = medical_tools.assess_diabetes_risk(patient_id)
        
        return jsonify({"patient_id": patient_id, "assessment": result})
        
    except Exception as e:
        logger.error(f"风险评估失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/safety/medication', methods=['POST'])
def check_medication():
    """
    用药安全检查接口
    
    请求体:
    {
        "patient_id": "患者ID",
        "medication": "药物名称"
    }
    """
    try:
        data = request.json
        patient_id = data.get('patient_id')
        medication = data.get('medication')
        
        if not patient_id or not medication:
            return jsonify({"error": "患者ID和药物名称不能为空"}), 400
        
        if not medical_tools:
            return jsonify({"error": "医疗工具未初始化"}), 500
        
        result = medical_tools.check_medication_safety(patient_id, medication)
        
        return jsonify({"result": result})
        
    except Exception as e:
        logger.error(f"用药安全检查失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({"error": "接口不存在"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"服务器内部错误: {error}")
    return jsonify({"error": "服务器内部错误"}), 500


if __name__ == "__main__":
    # 初始化应用
    initialize_app()
    
    # 启动Flask应用
    logger.info(f"启动Flask应用: {settings.flask_host}:{settings.flask_port}")
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.flask_debug,
        use_reloader=False  # 避免重复初始化
    )
