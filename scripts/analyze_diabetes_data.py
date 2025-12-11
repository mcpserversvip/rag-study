"""
Excel数据分析模块
分析《糖尿病病例统计.xlsx》中的胰岛素使用率数据分布
评分点: 4.1.2 Excel数据处理(3分)
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, List

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import logger


class DiabetesDataAnalyzer:
    """糖尿病数据分析器"""
    
    def __init__(self, excel_path: str):
        """
        初始化分析器
        
        Args:
            excel_path: Excel文件路径
        """
        self.excel_path = Path(excel_path)
        self.df = None
        
    def load_data(self):
        """加载Excel数据"""
        logger.info(f"加载Excel数据: {self.excel_path}")
        
        try:
            self.df = pd.read_excel(self.excel_path)
            logger.success(f"成功加载 {len(self.df)} 条记录")
            logger.info(f"列名: {list(self.df.columns)}")
            return True
        except Exception as e:
            logger.error(f"加载失败: {e}")
            return False
    
    def analyze_insulin_usage(self) -> Dict:
        """
        分析胰岛素使用率
        
        说明:
        - 空腹胰岛素和餐后2小时胰岛素都没有值或为空,说明没有使用胰岛素
        - 表格中的人都是糖尿病患者,共125人
        
        Returns:
            分析结果字典
        """
        logger.info("分析胰岛素使用率...")
        
        if self.df is None:
            logger.error("数据未加载")
            return {}
        
        # 查找胰岛素相关列
        insulin_columns = [col for col in self.df.columns if '胰岛素' in col]
        logger.info(f"找到胰岛素相关列: {insulin_columns}")
        
        # 判断是否使用胰岛素
        # 如果空腹胰岛素或餐后胰岛素有值,则认为使用了胰岛素
        if len(insulin_columns) >= 2:
            fasting_insulin = insulin_columns[0]
            postprandial_insulin = insulin_columns[1]
            
            # 使用胰岛素: 至少有一个胰岛素值不为空
            self.df['使用胰岛素'] = (
                self.df[fasting_insulin].notna() | 
                self.df[postprandial_insulin].notna()
            )
        else:
            logger.warning("未找到足够的胰岛素列")
            return {}
        
        # 统计使用率
        total_patients = len(self.df)
        insulin_users = self.df['使用胰岛素'].sum()
        non_users = total_patients - insulin_users
        usage_rate = (insulin_users / total_patients) * 100
        
        result = {
            "总患者数": total_patients,
            "使用胰岛素人数": int(insulin_users),
            "未使用胰岛素人数": int(non_users),
            "使用率": f"{usage_rate:.2f}%"
        }
        
        logger.success(f"胰岛素使用率分析完成: {result}")
        
        return result
    
    def analyze_by_gender(self) -> Dict:
        """
        按性别分析胰岛素使用情况
        
        Returns:
            性别分析结果
        """
        logger.info("按性别分析胰岛素使用情况...")
        
        if self.df is None or '使用胰岛素' not in self.df.columns:
            return {}
        
        # 查找性别列
        gender_col = None
        for col in self.df.columns:
            if '性别' in col:
                gender_col = col
                break
        
        if not gender_col:
            logger.warning("未找到性别列")
            return {}
        
        # 按性别统计
        gender_stats = self.df.groupby([gender_col, '使用胰岛素']).size().unstack(fill_value=0)
        
        result = {}
        for gender in gender_stats.index:
            total = gender_stats.loc[gender].sum()
            users = gender_stats.loc[gender].get(True, 0)
            rate = (users / total * 100) if total > 0 else 0
            
            result[gender] = {
                "总数": int(total),
                "使用胰岛素": int(users),
                "未使用胰岛素": int(total - users),
                "使用率": f"{rate:.2f}%"
            }
        
        logger.success(f"性别分析完成: {result}")
        return result
    
    def visualize_insulin_usage(self, output_path: str = None):
        """
        可视化胰岛素使用情况
        
        Args:
            output_path: 图片保存路径
        """
        logger.info("生成胰岛素使用率可视化...")
        
        if self.df is None or '使用胰岛素' not in self.df.columns:
            logger.error("数据未准备好")
            return
        
        # 创建图表
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 图1: 总体使用率饼图
        usage_counts = self.df['使用胰岛素'].value_counts()
        colors = ['#FF6B6B', '#4ECDC4']
        labels = ['未使用胰岛素', '使用胰岛素']
        
        axes[0].pie(
            usage_counts.values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        axes[0].set_title('糖尿病患者胰岛素使用率分布\n(总计125人)', fontsize=14, fontweight='bold')
        
        # 图2: 按性别分组的柱状图
        gender_col = None
        for col in self.df.columns:
            if '性别' in col:
                gender_col = col
                break
        
        if gender_col:
            gender_insulin = self.df.groupby([gender_col, '使用胰岛素']).size().unstack(fill_value=0)
            
            x = range(len(gender_insulin.index))
            width = 0.35
            
            axes[1].bar(
                [i - width/2 for i in x],
                gender_insulin.get(False, [0]*len(x)),
                width,
                label='未使用胰岛素',
                color='#FF6B6B'
            )
            axes[1].bar(
                [i + width/2 for i in x],
                gender_insulin.get(True, [0]*len(x)),
                width,
                label='使用胰岛素',
                color='#4ECDC4'
            )
            
            axes[1].set_xlabel('性别', fontsize=12)
            axes[1].set_ylabel('人数', fontsize=12)
            axes[1].set_title('不同性别胰岛素使用情况对比', fontsize=14, fontweight='bold')
            axes[1].set_xticks(x)
            axes[1].set_xticklabels(gender_insulin.index)
            axes[1].legend()
            axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图片
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.success(f"图表已保存到: {output_file}")
        
        plt.close()
    
    def generate_report(self, output_path: str = None) -> str:
        """
        生成分析报告
        
        Args:
            output_path: 报告保存路径
            
        Returns:
            报告文本
        """
        logger.info("生成分析报告...")
        
        # 总体分析
        overall = self.analyze_insulin_usage()
        
        # 性别分析
        gender = self.analyze_by_gender()
        
        # 生成报告
        report = "="*80 + "\n"
        report += "糖尿病患者胰岛素使用率数据分析报告\n"
        report += "="*80 + "\n\n"
        
        report += "【数据来源】\n"
        report += f"文件: {self.excel_path.name}\n"
        report += f"患者总数: {overall['总患者数']}人\n\n"
        
        report += "【总体分析】\n"
        report += f"- 使用胰岛素: {overall['使用胰岛素人数']}人 ({overall['使用率']})\n"
        report += f"- 未使用胰岛素: {overall['未使用胰岛素人数']}人\n\n"
        
        if gender:
            report += "【性别分布分析】\n"
            for sex, stats in gender.items():
                report += f"\n{sex}:\n"
                report += f"  - 总数: {stats['总数']}人\n"
                report += f"  - 使用胰岛素: {stats['使用胰岛素']}人 ({stats['使用率']})\n"
                report += f"  - 未使用胰岛素: {stats['未使用胰岛素']}人\n"
        
        report += "\n" + "="*80 + "\n"
        report += "【分析说明】\n"
        report += "- 判断标准: 空腹胰岛素或餐后2小时胰岛素有测量值,视为使用胰岛素\n"
        report += "- 数据来源: 糖尿病病例统计Excel文件\n"
        report += "="*80 + "\n"
        
        # 保存报告
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.success(f"报告已保存到: {output_file}")
        
        return report


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("糖尿病数据分析")
    logger.info("="*80)
    
    # Excel文件路径
    excel_file = project_root / 'data' / '糖尿病病例统计.xlsx'
    
    if not excel_file.exists():
        logger.error(f"Excel文件不存在: {excel_file}")
        return
    
    # 创建分析器
    analyzer = DiabetesDataAnalyzer(str(excel_file))
    
    # 加载数据
    if not analyzer.load_data():
        return
    
    # 分析胰岛素使用率
    overall_result = analyzer.analyze_insulin_usage()
    
    # 按性别分析
    gender_result = analyzer.analyze_by_gender()
    
    # 生成可视化
    output_dir = project_root / 'temp' / 'analysis'
    analyzer.visualize_insulin_usage(str(output_dir / 'insulin_usage.png'))
    
    # 生成报告
    report = analyzer.generate_report(str(output_dir / 'analysis_report.txt'))
    
    # 打印报告
    print("\n" + report)
    
    logger.success("="*80)
    logger.success("✅ 数据分析完成!")
    logger.success("="*80)


if __name__ == "__main__":
    main()
