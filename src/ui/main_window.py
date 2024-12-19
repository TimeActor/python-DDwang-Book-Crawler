from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                           QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt
from src.ui.crawler_panel import CrawlerPanel
from src.ui.analysis_panel import AnalysisPanel
from src.ui.export_panel import ExportPanel
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("当当网图书数据分析系统")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.logger = logging.getLogger(__name__)
        
    def setup_ui(self):
        """初始化UI"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 添加爬虫面板
        self.crawler_panel = CrawlerPanel()
        tab_widget.addTab(self.crawler_panel, "数据采集")
        
        # 添加分析面板
        self.analysis_panel = AnalysisPanel()
        tab_widget.addTab(self.analysis_panel, "数据分析")
        
        # 添加导出面板
        self.export_panel = ExportPanel()
        tab_widget.addTab(self.export_panel, "数据导出")
        
        layout.addWidget(tab_widget)
        
        # 添加状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪") 