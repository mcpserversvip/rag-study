"""
数据库初始化脚本
执行DDL创建表结构,并导入CSV数据
"""
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.database import get_db_connector
from src.utils.logger import logger


def test_connection():
    """测试数据库连接"""
    logger.info("测试数据库连接...")
    
    try:
        db = get_db_connector()
        if db.test_connection():
            logger.success("✅ 数据库连接成功")
            return True
        else:
            logger.error("❌ 数据库连接失败")
            return False
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False


def drop_all_tables():
    """
    删除数据库中所有表(支持重复执行)
    """
    logger.info("删除所有表...")
    
    db = get_db_connector()
    
    # 禁用外键检查
    db.execute_update("SET FOREIGN_KEY_CHECKS = 0")
    
    # 获取所有表名
    tables = db.execute_query("SHOW TABLES")
    
    if tables:
        for table in tables:
            table_name = list(table.values())[0]
            try:
                db.execute_update(f"DROP TABLE IF EXISTS `{table_name}`")
                logger.debug(f"删除表: {table_name}")
            except Exception as e:
                logger.warning(f"删除表{table_name}失败: {e}")
    
    # 重新启用外键检查
    db.execute_update("SET FOREIGN_KEY_CHECKS = 1")
    
    logger.success(f"✅ 已删除 {len(tables) if tables else 0} 个表")


def execute_ddl(ddl_file: str):
    """
    执行DDL文件创建表结构
    
    Args:
        ddl_file: DDL文件路径
    """
    logger.info(f"执行DDL文件: {ddl_file}")
    
    try:
        # 读取DDL文件
        with open(ddl_file, 'r', encoding='utf-8') as f:
            ddl_content = f.read()
        
        # 分割SQL语句
        statements = [s.strip() for s in ddl_content.split(';') if s.strip()]
        
        db = get_db_connector()
        
        # 执行每条语句
        success_count = 0
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    db.execute_update(statement)
                    success_count += 1
                    logger.debug(f"执行语句 {i}/{len(statements)}")
                except Exception as e:
                    # 忽略表已存在的错误
                    if "already exists" in str(e).lower():
                        logger.debug(f"表已存在,跳过: {statement[:50]}...")
                        success_count += 1
                    else:
                        logger.error(f"执行失败: {e}")
        
        logger.success(f"✅ DDL执行完成,成功执行 {success_count}/{len(statements)} 条语句")
        
    except Exception as e:
        logger.error(f"❌ DDL执行失败: {e}")
        raise


def import_csv_data(csv_dir: str):
    """
    导入CSV数据到数据库
    
    Args:
        csv_dir: CSV文件目录
    """
    logger.info(f"导入CSV数据: {csv_dir}")
    
    csv_path = Path(csv_dir)
    if not csv_path.exists():
        logger.error(f"CSV目录不存在: {csv_dir}")
        return
    
    # CSV文件到表名的映射
    table_mapping = {
        'patient_info': 'patient_info',
        'medical_records': 'medical_records',
        'lab_results': 'lab_results',
        'medication_records': 'medication_records',
        'diagnosis_records': 'diagnosis_records',
        'hypertension_risk_assessment': 'hypertension_risk_assessment',
        'diabetes_control_assessment': 'diabetes_control_assessment',
        'guideline_recommendations': 'guideline_recommendations',
        'system_logs': 'system_logs'
    }
    
    # 按照外键依赖顺序导入（无依赖的表优先）
    import_order = [
        'patient_info',           # 无外键依赖
        'guideline_recommendations',  # 无外键依赖
        'system_logs',            # 无外键依赖
        'medical_records',        # 依赖 patient_info
        'lab_results',            # 依赖 patient_info, medical_records
        'medication_records',     # 依赖 patient_info, medical_records
        'diagnosis_records',      # 依赖 patient_info, medical_records
        'hypertension_risk_assessment',  # 依赖 patient_info
        'diabetes_control_assessment',   # 依赖 patient_info
    ]
    
    db = get_db_connector()
    
    # 遍历CSV文件（按依赖顺序）
    csv_files = list(csv_path.glob('*.csv'))
    logger.info(f"找到 {len(csv_files)} 个CSV文件")
    
    # 按导入顺序排序CSV文件
    def get_import_priority(csv_file):
        file_name = csv_file.stem
        for i, table_key in enumerate(import_order):
            if table_key in file_name:
                return i
        return len(import_order)  # 未知文件放最后
    
    csv_files.sort(key=get_import_priority)
    
    for csv_file in csv_files:
        # 从文件名提取表名
        file_name = csv_file.stem
        table_name = None
        
        for key, value in table_mapping.items():
            if key in file_name:
                table_name = value
                break
        
        if not table_name:
            logger.warning(f"跳过未知文件: {csv_file.name}")
            continue
        
        try:
            logger.info(f"导入 {csv_file.name} -> {table_name}")
            
            # 读取CSV
            df = pd.read_csv(csv_file)
            logger.info(f"  读取 {len(df)} 条记录")
            
            # 清空表(可选)
            # db.execute_update(f"TRUNCATE TABLE {table_name}")
            
            # 检查表是否有数据
            count_result = db.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            existing_count = count_result[0]['count'] if count_result else 0
            
            if existing_count > 0:
                logger.info(f"  表 {table_name} 已有 {existing_count} 条记录,跳过导入")
                continue
            
            # 批量插入数据
            # 排除 GENERATED ALWAYS 列（如 bmi），这些列不能直接插入值
            excluded_columns = ['bmi']  # GENERATED ALWAYS 列，由数据库自动计算
            columns = [col for col in df.columns.tolist() if col not in excluded_columns]
            placeholders = ', '.join([f':{col}' for col in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            inserted = 0
            for _, row in df.iterrows():
                try:
                    # 只取需要插入的列，排除 GENERATED 列
                    params = {col: row[col] for col in columns}
                    # 处理NaN值
                    for key, value in params.items():
                        if pd.isna(value):
                            params[key] = None
                    
                    db.execute_update(insert_sql, params)
                    inserted += 1
                except Exception as e:
                    logger.warning(f"  插入失败: {e}")
            
            logger.success(f"  ✅ 成功导入 {inserted} 条记录到 {table_name}")
            
        except Exception as e:
            logger.error(f"  ❌ 导入失败: {e}")


def verify_data():
    """验证数据导入"""
    logger.info("验证数据导入...")
    
    tables = [
        'patient_info',
        'medical_records',
        'lab_results',
        'medication_records',
        'diagnosis_records',
        'hypertension_risk_assessment',
        'diabetes_control_assessment',
        'guideline_recommendations'
    ]
    
    db = get_db_connector()
    
    print("\n" + "="*80)
    print("数据统计:")
    print("="*80)
    
    for table in tables:
        try:
            result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            print(f"{table:40s}: {count:6d} 条记录")
        except Exception as e:
            print(f"{table:40s}: 错误 - {e}")
    
    print("="*80)


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始初始化数据库")
    logger.info("="*80)
    
    # 1. 测试连接
    if not test_connection():
        logger.error("数据库连接失败,请检查配置和Docker容器状态")
        return
    
    # 2. 删除所有表
    drop_all_tables()

    # 2. 执行DDL
    ddl_file = project_root / 'db' / 'ddl.sql'
    if ddl_file.exists():
        execute_ddl(str(ddl_file))
    else:
        logger.error(f"DDL文件不存在: {ddl_file}")
        return
    
    # 3. 导入CSV数据
    csv_dir = project_root / 'db' / 'data-csv'
    if csv_dir.exists():
        import_csv_data(str(csv_dir))
    else:
        logger.warning(f"CSV目录不存在: {csv_dir}")
    
    # 4. 验证数据
    verify_data()
    
    logger.success("="*80)
    logger.success("✅ 数据库初始化完成!")
    logger.success("="*80)


if __name__ == "__main__":
    main()
