"""
更新 lab_results CSV 文件中的 record_id 字段

此脚本从 medication_records 和 diagnosis_records CSV 文件中读取 patient_id 与 record_id 的映射关系，
并将对应的 record_id 更新到 lab_results CSV 文件中。

特性:
- 支持从多个数据源文件中提取映射关系
- record_id 保存为整数类型
- 支持 --clear 参数清除现有 record_id 值后重新更新
- 支持重复执行：如果 record_id 已有值则不更新（除非使用 --clear）
- 需要在 init_database.py 之前执行

使用方法:
    python scripts/update_lab_results_record_id.py          # 正常更新
    python scripts/update_lab_results_record_id.py --clear  # 清除后重新更新
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_patient_record_mapping_from_file(csv_file: str, file_type: str = "数据") -> dict:
    """
    从 CSV 文件中提取 patient_id 到 record_id 的映射

    Args:
        csv_file: CSV 文件路径
        file_type: 文件类型描述（用于日志输出）

    Returns:
        dict: patient_id -> record_id 的映射字典
    """
    print(f"正在读取{file_type}文件: {csv_file}")
    
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # 创建 patient_id -> record_id 的映射
    # 如果同一个 patient_id 有多条记录，取第一个 record_id
    mapping = {}
    for _, row in df.iterrows():
        patient_id = str(row['patient_id'])
        record_id = row['record_id']
        
        # 如果这个 patient_id 还没有映射，添加它
        if patient_id not in mapping:
            mapping[patient_id] = record_id
    
    print(f"  -> 已提取 {len(mapping)} 个患者的 record_id 映射")
    return mapping


def get_combined_patient_record_mapping(data_dir: Path) -> dict:
    """
    从多个数据源文件中合并提取 patient_id 到 record_id 的映射

    优先级：medication_records > diagnosis_records
    后读取的文件不会覆盖已有的映射

    Args:
        data_dir: 数据文件目录

    Returns:
        dict: patient_id -> record_id 的合并映射字典
    """
    combined_mapping = {}
    
    # 1. 从 medication_records 获取映射
    medication_files = list(data_dir.glob("medication_records_*.csv"))
    if medication_files:
        medication_file = sorted(medication_files)[-1]
        med_mapping = get_patient_record_mapping_from_file(str(medication_file), "用药记录")
        combined_mapping.update(med_mapping)
    else:
        print("警告: 未找到 medication_records CSV 文件")
    
    # 2. 从 diagnosis_records 获取映射（补充未覆盖的患者）
    diagnosis_files = list(data_dir.glob("diagnosis_records_*.csv"))
    if diagnosis_files:
        diagnosis_file = sorted(diagnosis_files)[-1]
        diag_mapping = get_patient_record_mapping_from_file(str(diagnosis_file), "诊断记录")
        
        # 只添加 medication_records 中没有的映射
        new_count = 0
        for patient_id, record_id in diag_mapping.items():
            if patient_id not in combined_mapping:
                combined_mapping[patient_id] = record_id
                new_count += 1
        
        print(f"  -> 从诊断记录补充了 {new_count} 个新患者的映射")
    else:
        print("警告: 未找到 diagnosis_records CSV 文件")
    
    print(f"\n合并后共有 {len(combined_mapping)} 个患者的 record_id 映射")
    return combined_mapping


def clear_record_id(lab_results_file: str) -> int:
    """
    清除 lab_results 文件中的 record_id 字段值

    Args:
        lab_results_file: lab_results CSV 文件路径

    Returns:
        int: 清除的记录数
    """
    print(f"正在清除 record_id 字段: {lab_results_file}")
    
    df = pd.read_csv(lab_results_file, encoding='utf-8')
    
    # 统计有值的记录数
    has_value_count = df['record_id'].notna().sum()
    
    # 清除 record_id 字段
    df['record_id'] = np.nan
    
    # 保存文件
    df.to_csv(lab_results_file, index=False, encoding='utf-8')
    print(f"  -> 已清除 {has_value_count} 条记录的 record_id 值")
    
    return has_value_count


def update_lab_results_record_id(
    lab_results_file: str,
    patient_record_mapping: dict,
    output_file: str = None
) -> tuple:
    """
    更新 lab_results 文件中的 record_id 字段

    Args:
        lab_results_file: lab_results CSV 文件路径
        patient_record_mapping: patient_id -> record_id 的映射字典
        output_file: 输出文件路径，如果为 None 则覆盖原文件

    Returns:
        tuple: (更新的记录数, 跳过的记录数, 未找到映射的记录数)
    """
    print(f"正在读取检验结果文件: {lab_results_file}")
    
    df = pd.read_csv(lab_results_file, encoding='utf-8')
    
    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    not_found_patients = set()
    
    for idx, row in df.iterrows():
        patient_id = str(row['patient_id'])
        current_record_id = row['record_id']
        
        # 检查 record_id 是否已有值（非空、非NaN）
        if pd.notna(current_record_id) and str(current_record_id).strip() != '':
            skipped_count += 1
            continue
        
        # 查找对应的 record_id，转换为整数
        if patient_id in patient_record_mapping:
            record_id = patient_record_mapping[patient_id]
            # 确保 record_id 是整数类型
            df.at[idx, 'record_id'] = int(record_id)
            updated_count += 1
        else:
            not_found_count += 1
            not_found_patients.add(patient_id)
    
    # 将 record_id 列转换为可空整数类型
    df['record_id'] = df['record_id'].astype('Int64')
    
    # 保存更新后的文件
    if output_file is None:
        output_file = lab_results_file
    
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"已保存更新后的文件: {output_file}")
    
    # 打印未找到映射的患者ID
    if not_found_patients:
        print(f"\n警告: 以下 {len(not_found_patients)} 个患者ID在所有数据源中未找到对应的record_id:")
        for pid in sorted(not_found_patients)[:10]:  # 只显示前10个
            print(f"  - {pid}")
        if len(not_found_patients) > 10:
            print(f"  ... 还有 {len(not_found_patients) - 10} 个")
    
    return updated_count, skipped_count, not_found_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="更新 lab_results CSV 文件中的 record_id 字段")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="清除所有现有的 record_id 值，然后重新更新"
    )
    args = parser.parse_args()

    # 定义文件路径
    data_dir = project_root / "db" / "data-csv"
    
    # 查找 lab_results 文件
    lab_results_files = list(data_dir.glob("lab_results_*.csv"))
    if not lab_results_files:
        print("错误: 未找到 lab_results CSV 文件")
        sys.exit(1)
    
    # 使用最新的文件
    lab_results_file = sorted(lab_results_files)[-1]
    
    print("=" * 60)
    print("更新 lab_results record_id 工具")
    print("=" * 60)
    print(f"检验结果文件: {lab_results_file.name}")
    print("-" * 60)
    
    # Step 1: 从多个数据源获取 patient_id -> record_id 映射
    patient_record_mapping = get_combined_patient_record_mapping(data_dir)
    
    print("-" * 60)
    
    # Step 2: 如果指定了 --clear 参数，先清除现有的 record_id 值
    if args.clear:
        print("\n[清除模式] 正在清除现有 record_id 值...")
        clear_record_id(str(lab_results_file))
        print("-" * 60)
    
    # Step 3: 更新 lab_results 的 record_id
    updated, skipped, not_found = update_lab_results_record_id(
        str(lab_results_file),
        patient_record_mapping
    )
    
    # 打印总结
    print("\n" + "=" * 60)
    print("执行结果统计")
    print("=" * 60)
    print(f"已更新的记录数: {updated}")
    print(f"已跳过的记录数（record_id已有值）: {skipped}")
    print(f"未找到映射的记录数: {not_found}")
    print("=" * 60)
    
    if skipped > 0:
        print(f"\n提示: {skipped} 条记录的 record_id 已有值，未进行修改")
    
    if updated > 0:
        print(f"\n✓ 成功更新 {updated} 条记录的 record_id")
    else:
        print("\n✓ 所有记录的 record_id 均已有值，无需更新")


if __name__ == "__main__":
    main()
