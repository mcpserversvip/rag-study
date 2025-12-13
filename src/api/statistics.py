import pandas as pd
from flask import Blueprint, jsonify, request
from pathlib import Path
from src.utils.logger import logger
from src.config import settings

statistics_bp = Blueprint('statistics', __name__)

EXCEL_FILE_PATH = Path(settings.project_root) / 'data' / '糖尿病病例统计.xlsx'


def classify_insulin_usage(row, col_fasting, col_postprandial):
    """
    分类胰岛素使用情况
    - 两列都为空 → 'not_using' (未使用胰岛素)
    - 两列都有值 → 'using' (使用胰岛素)
    - 只有一列有值 → 'not_measured' (未测量/数据不完整)
    """
    def is_empty(val):
        """判断值是否为空：NaN, None 或 '/'"""
        return pd.isna(val) or str(val).strip() == '/'

    fasting_empty = is_empty(row[col_fasting])
    postprandial_empty = is_empty(row[col_postprandial])
    
    if fasting_empty and postprandial_empty:
        return 'not_using'
    elif not fasting_empty and not postprandial_empty:
        return 'using'
    else:
        return 'not_measured'


def get_age_group(age):
    """年龄分组"""
    if age < 40:
        return '<40岁'
    elif age < 60:
        return '40-60岁'
    elif age < 80:
        return '60-80岁'
    else:
        return '≥80岁'


def get_height_group(height):
    """身高分组 (单位: 米)"""
    if height < 1.55:
        return '<1.55m'
    elif height < 1.70:
        return '1.55-1.70m'
    else:
        return '≥1.70m'


def get_weight_group(weight):
    """体重分组 (单位: kg)"""
    if weight < 50:
        return '<50kg'
    elif weight < 70:
        return '50-70kg'
    elif weight < 90:
        return '70-90kg'
    else:
        return '≥90kg'


@statistics_bp.route('/api/statistics/insulin', methods=['GET'])
def get_insulin_statistics():
    """
    获取胰岛素使用统计，支持多维度分组
    
    Query Parameters:
        dimension: 分组维度，可选值: gender(默认), age, height, weight
    """
    try:
        if not EXCEL_FILE_PATH.exists():
            logger.error(f"Data file not found: {EXCEL_FILE_PATH}")
            return jsonify({"error": "数据文件未找到"}), 404

        # 获取分组维度参数
        dimension = request.args.get('dimension', 'gender')
        valid_dimensions = ['gender', 'age', 'height', 'weight']
        if dimension not in valid_dimensions:
            return jsonify({"error": f"无效的维度参数，可选: {valid_dimensions}"}), 400

        # 读取Excel文件
        df = pd.read_excel(EXCEL_FILE_PATH)
        
        # 列名定义
        col_gender = '性别 (Female=1, Male=2)'
        col_age = '年龄 (years)'
        col_height = '身高 (m)'
        col_weight = '体重 (kg)'
        col_fasting = '空腹胰岛素 (pmol/L)'
        col_postprandial = '餐后2小时胰岛素 (pmol/L)'
        
        # 验证必需列
        required_cols = [col_gender, col_age, col_height, col_weight, col_fasting, col_postprandial]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing columns: {missing_cols}")
            return jsonify({"error": f"数据文件缺少列: {missing_cols}"}), 500

        # 分类胰岛素使用情况
        df['insulin_status'] = df.apply(
            lambda row: classify_insulin_usage(row, col_fasting, col_postprandial), 
            axis=1
        )
        
        # 计算总体分类统计
        classification = {
            "using_insulin": int((df['insulin_status'] == 'using').sum()),
            "not_using_insulin": int((df['insulin_status'] == 'not_using').sum()),
            "not_measured": int((df['insulin_status'] == 'not_measured').sum())
        }

        # 根据维度分组
        if dimension == 'gender':
            df['group'] = df[col_gender].map({1: '女性', 2: '男性'})
            group_order = ['男性', '女性']
        elif dimension == 'age':
            df['group'] = df[col_age].apply(get_age_group)
            group_order = ['<40岁', '40-60岁', '60-80岁', '≥80岁']
        elif dimension == 'height':
            df['group'] = df[col_height].apply(get_height_group)
            group_order = ['<1.55m', '1.55-1.70m', '≥1.70m']
        elif dimension == 'weight':
            df['group'] = df[col_weight].apply(get_weight_group)
            group_order = ['<50kg', '50-70kg', '70-90kg', '≥90kg']

        # 按分组统计
        distribution = []
        for group_label in group_order:
            group_df = df[df['group'] == group_label]
            if len(group_df) > 0:
                distribution.append({
                    "label": group_label,
                    "using": int((group_df['insulin_status'] == 'using').sum()),
                    "not_using": int((group_df['insulin_status'] == 'not_using').sum()),
                    "not_measured": int((group_df['insulin_status'] == 'not_measured').sum()),
                    "total": len(group_df)
                })

        # 构建响应
        stats = {
            "total_patients": len(df),
            "note": "所有患者均为糖尿病患者",
            "classification": classification,
            "dimension": dimension,
            "dimension_label": {
                "gender": "性别",
                "age": "年龄段", 
                "height": "身高",
                "weight": "体重"
            }.get(dimension, dimension),
            "distribution": distribution
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error processing statistics: {e}")
        return jsonify({"error": str(e)}), 500
