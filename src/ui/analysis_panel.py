from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QTabWidget, QScrollArea,
                           QGridLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from ..analysis.book_analyzer import BookAnalyzer
from ..visualization.data_visualizer import DataVisualizer
from ..database.db_manager import DatabaseManager
import pandas as pd
import logging
from pathlib import Path
import shutil

class AnalysisWorker(QThread):
    """数据分析工作线程"""
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer
        
    def run(self):
        try:
            report = self.analyzer.generate_summary_report()
            self.finished.emit(True, report)
        except Exception as e:
            self.finished.emit(False, {"error": str(e)})

class AnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.analyzer = BookAnalyzer(self.db_manager)
        self.visualizer = DataVisualizer()
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        # 分析按钮
        self.analyze_button = QPushButton("开始分析")
        self.analyze_button.clicked.connect(self.start_analysis)
        control_layout.addWidget(self.analyze_button)
        
        # 导出按钮
        self.export_button = QPushButton("导出报告")
        self.export_button.clicked.connect(self.export_report)
        control_layout.addWidget(self.export_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 创建标签页显示不同的分析结果
        self.tab_widget = QTabWidget()
        
        # 数据表格页
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout(self.table_tab)
        self.create_data_table()
        self.tab_widget.addTab(self.table_tab, "数据表格")
        
        # 图表展示页
        self.chart_tab = QWidget()
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # 创建内容widget
        chart_content = QWidget()
        self.chart_layout = QGridLayout(chart_content)
        
        # 设置滚动区域的widget
        scroll.setWidget(chart_content)
        
        # 创建主布局
        chart_main_layout = QVBoxLayout(self.chart_tab)
        chart_main_layout.addWidget(scroll)
        
        self.tab_widget.addTab(self.chart_tab, "图表展示")
        
        # 统计信息页
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_tab)
        self.tab_widget.addTab(self.stats_tab, "统计信息")
        
        # 添加到主布局
        layout.addWidget(self.tab_widget)
        
    def create_data_table(self):
        """创建数据表格"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "书名", "作者", "价格", "评分", "分类", "出版社"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_layout.addWidget(self.table)
        
    def update_data_table(self, df: pd.DataFrame):
        """更新数据表格"""
        self.table.setRowCount(0)
        if df is None or df.empty:
            return
            
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(row['title'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['author'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['price'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['rating'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row.get('category', ''))))
            self.table.setItem(i, 5, QTableWidgetItem(str(row.get('publisher', ''))))

    def update_stats_display(self, stats: dict):
        """更新统计信息显示"""
        # 清空原有内容
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setProperty("deleteLater", True)
        
        if not stats:
            return
            
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # 基本统计信息
        if 'basic_stats' in stats:
            basic = stats['basic_stats']
            content_layout.addWidget(QLabel("基本统计信息"))
            content_layout.addWidget(QLabel(f"总图书数量: {basic['total_books']}"))
            content_layout.addWidget(QLabel(f"平均价格: {basic['avg_price']:.2f}元"))
            content_layout.addWidget(QLabel(f"最高价格: {basic['max_price']:.2f}元"))
            content_layout.addWidget(QLabel(f"最低价格: {basic['min_price']:.2f}元"))
            content_layout.addWidget(QLabel(f"平均评分: {basic['avg_rating']:.2f}"))
        
        # 出版社统计
        if 'publisher_stats' in stats:
            content_layout.addWidget(QLabel("\n出版社TOP10"))
            for pub in stats['publisher_stats'][:10]:
                content_layout.addWidget(QLabel(
                    f"{pub['publisher']}: {pub['book_count']}本, "
                    f"均价{pub['avg_price']:.2f}元, "
                    f"均分{pub['avg_rating']:.2f}"
                ))
        
        # 分类统计
        if 'category_stats' in stats:
            content_layout.addWidget(QLabel("\n图书分类统计"))
            for cat in stats['category_stats']:
                content_layout.addWidget(QLabel(
                    f"{cat['category']}: {cat['book_count']}本, "
                    f"均价{cat['avg_price']:.2f}元"
                ))
        
        # 关键词统计
        if 'keyword_stats' in stats:
            content_layout.addWidget(QLabel("\n热门关键词"))
            keywords = list(stats['keyword_stats'].items())[:10]
            for word, count in keywords:
                content_layout.addWidget(QLabel(f"{word}: {count}次"))
        
        scroll.setWidget(content)
        self.stats_layout.addWidget(scroll)

    def start_analysis(self):
        """开始数据分析"""
        try:
            # 获取数据
            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query("SELECT * FROM books", conn)
            
            # 生成分析报告
            report = self.analyzer.generate_summary_report()
            
            # 更新所有分析结果
            self.update_stats_display(report)  # 显示所有统计信息
            self.visualizer.generate_all_plots(self.analyzer)  # 生成图表
            self.update_charts()  # 显示图表
            self.update_data_table(df)  # 更新数据表格
            
            self.logger.info("数据分析完成")
            
        except Exception as e:
            self.logger.error(f"数据分析失败: {str(e)}")
            QMessageBox.warning(self, "分析失败", f"数据分析时出错：\n{str(e)}")

    def update_charts(self):
        """更新图表显示"""
        try:
            # 清空原有图表
            for i in reversed(range(self.chart_layout.count())): 
                self.chart_layout.itemAt(i).widget().setProperty("deleteLater", True)
            
            # 加载并显示分类分布图
            chart_label = QLabel()
            chart_label.setAlignment(Qt.AlignCenter)
            
            # 加载图片并保持原始分辨率
            pixmap = QPixmap(str(self.visualizer.save_dir / 'category_distribution.png'))
            
            # 获取当前窗口大小
            window_width = self.width()
            window_height = self.height()
            
            # 计算合适的图片大小（使用窗口大小的70%）
            target_size = min(window_width * 0.7, window_height * 0.7)
            
            # 设置合适的显示大小，保持纵横比
            scaled_pixmap = pixmap.scaled(int(target_size), int(target_size), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            chart_label.setPixmap(scaled_pixmap)
            
            # 添加到布局
            self.chart_layout.addWidget(chart_label, 0, 0, Qt.AlignCenter)
            
            # 设置布局间距和边距
            self.chart_layout.setSpacing(10)
            self.chart_layout.setContentsMargins(10, 10, 10, 10)
                
        except Exception as e:
            self.logger.error(f"更新图表失败: {str(e)}")

    def resizeEvent(self, event):
        """窗口大小改变时重新调整图表大小"""
        super().resizeEvent(event)
        self.update_charts()

    def export_report(self):
        """导出分析报告"""
        try:
            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "选择保存位置",
                str(Path.home() / "分析报告.html"),
                "HTML files (*.html)"
            )
            
            if not file_path:
                return
            
            # 创建报告目录
            report_dir = Path(file_path).parent / "report_files"
            report_dir.mkdir(exist_ok=True)
            
            # 复制图片到报告目录
            chart_path = self.visualizer.save_dir / 'category_distribution.png'
            chart_dest = report_dir / 'category_distribution.png'
            shutil.copy2(chart_path, chart_dest)
            
            # 获取最新数据
            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query("SELECT * FROM books", conn)
            
            # 生成分析报告
            report = self.analyzer.generate_summary_report()
            
            # 生成HTML报告
            html_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>当当网图书数据分析报告</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f5f5f5; }}
                    img {{ max-width: 100%; height: auto; margin: 10px 0; display: block; margin: 0 auto; }}
                    .chart-container {{ text-align: center; }}
                    ul {{ list-style-type: none; padding-left: 0; }}
                    li {{ margin: 5px 0; }}
                </style>
            </head>
            <body>
                <h1>当当网图书数据分析报告</h1>
                <p>生成时间：{report['generated_at']}</p>
                
                <div class="section">
                    <h2>基本统计信息</h2>
                    <ul>
                        <li>总图书数量：{report['basic_stats']['total_books']}本</li>
                        <li>平均价格：{report['basic_stats']['avg_price']:.2f}元</li>
                        <li>最高价格：{report['basic_stats']['max_price']:.2f}元</li>
                        <li>最低价格：{report['basic_stats']['min_price']:.2f}元</li>
                        <li>平均评分：{report['basic_stats']['avg_rating']:.2f}</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>出版社统计（TOP10）</h2>
                    <table>
                        <tr>
                            <th>出版社</th>
                            <th>图书数量</th>
                            <th>平均价格</th>
                            <th>平均评分</th>
                        </tr>
                        {''.join(f'''
                        <tr>
                            <td>{pub['publisher']}</td>
                            <td>{pub['book_count']}本</td>
                            <td>{pub['avg_price']:.2f}元</td>
                            <td>{pub['avg_rating']:.2f}</td>
                        </tr>
                        ''' for pub in report['publisher_stats'][:10])}
                    </table>
                </div>
                
                <div class="section">
                    <h2>图书分类统计</h2>
                    <table>
                        <tr>
                            <th>分类</th>
                            <th>图书数量</th>
                            <th>平均价格</th>
                        </tr>
                        {''.join(f'''
                        <tr>
                            <td>{cat['category']}</td>
                            <td>{cat['book_count']}本</td>
                            <td>{cat['avg_price']:.2f}元</td>
                        </tr>
                        ''' for cat in report['category_stats'])}
                    </table>
                </div>
                
                <div class="section">
                    <h2>热门关键词（TOP10）</h2>
                    <ul>
                        {''.join(f'<li>{word}: {count}次</li>' 
                                for word, count in list(report['keyword_stats'].items())[:10])}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>分类分布图</h2>
                    <div class="chart-container">
                        <img src="report_files/category_distribution.png" alt="分类分布图">
                    </div>
                </div>
                
                <div class="section">
                    <h2>原始数据</h2>
                    {df.to_html(index=False, classes='data-table')}
                </div>
            </body>
            </html>
            """
            
            # 保存HTML报告
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 显示成功消息
            QMessageBox.information(self, "导出成功", 
                                  f"分析报告已保存至：\n{file_path}\n"
                                  f"相关文件保存在：\n{report_dir}")
            
        except Exception as e:
            self.logger.error(f"导出报告失败: {str(e)}")
            QMessageBox.warning(self, "导出失��", f"导出报告时出错：\n{str(e)}")