import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import pandas as pd
import logging
from pathlib import Path
from src.utils.path_manager import PathManager
import numpy as np

class DataVisualizer:
    def __init__(self):
        paths = PathManager.initialize_project_directories()
        self.save_dir = paths['visualizations_dir']
        self.logger = logging.getLogger(__name__)
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置DPI和图表大小（调小一些）
        plt.rcParams['figure.dpi'] = 100  # 降低DPI
        plt.rcParams['figure.figsize'] = [8, 8]  # 减小图表尺寸
        
        # 设置字体大小
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14

    def _save_plot(self, filename: str):
        """保存图表"""
        try:
            filepath = self.save_dir / filename
            plt.savefig(filepath, 
                       dpi=300,
                       bbox_inches='tight',
                       pad_inches=0.2,
                       facecolor='white',
                       transparent=False)
            plt.close()
            self.logger.info(f"图表已保存至: {filepath}")
        except Exception as e:
            self.logger.error(f"保存图表失败: {str(e)}")

    def plot_category_distribution(self, distribution: Dict[str, int]):
        """绘制图书分类分布图"""
        plt.figure(figsize=(8, 8))  # 使用更小的尺寸
        
        # 计算百分比
        total = sum(distribution.values())
        categories = list(distribution.keys())
        counts = list(distribution.values())
        
        # 设置颜色
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(categories)))
        
        # 绘制饼图
        plt.pie(counts, 
               labels=categories,
               colors=colors,
               autopct='%1.1f%%',
               startangle=90,
               pctdistance=0.85)
        
        # 添加标题
        plt.title('图书分类分布', pad=20, fontsize=14, fontweight='bold')
        
        # 添加图例
        plt.legend(categories, 
                  title="分类",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.axis('equal')  # 保持圆形
        plt.tight_layout()
        self._save_plot('category_distribution.png')

    def generate_all_plots(self, analyzer):
        """生成所有可视化图表"""
        try:
            # 只生成分类分布图
            category_stats = analyzer.analyze_categories()
            category_dist = {row['category']: row['book_count'] 
                           for _, row in category_stats.iterrows()}
            self.plot_category_distribution(category_dist)
            
            self.logger.info("图表生成完成")
            return True
            
        except Exception as e:
            self.logger.error(f"生成图表时出错: {str(e)}")
            return False 