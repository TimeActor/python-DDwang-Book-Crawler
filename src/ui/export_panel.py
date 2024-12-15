from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QFileDialog, QCheckBox,
                           QGroupBox, QFormLayout, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime
from ..database.db_manager import DatabaseManager

class ExportWorker(QThread):
    """数据导出工作线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, db_manager, export_type, file_path, options):
        super().__init__()
        self.db_manager = db_manager
        self.export_type = export_type
        self.file_path = file_path
        self.options = options
        
    def run(self):
        try:
            if self.export_type == "CSV":
                success = self.db_manager.export_to_csv(self.file_path)
            elif self.export_type == "Excel":
                success = self.export_to_excel()
            elif self.export_type == "JSON":
                success = self.export_to_json()
            else:
                raise ValueError(f"不支持的导出格式: {self.export_type}")
                
            self.finished.emit(success, "导出成功" if success else "导出失败")
            
        except Exception as e:
            self.finished.emit(False, f"导出错误: {str(e)}")
            
    def export_to_excel(self):
        """导出为Excel格式"""
        try:
            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query("SELECT * FROM books", conn)
                
                # 创建Excel写入器
                with pd.ExcelWriter(self.file_path) as writer:
                    # 导出原始数据
                    if self.options.get('export_raw', True):
                        df.to_excel(writer, sheet_name='原始数据', index=False)
                        
                    # 导出统计数据
                    if self.options.get('export_stats', True):
                        # 价格统计
                        price_stats = df['price'].describe()
                        price_stats.to_excel(writer, sheet_name='统计数据', startrow=0)
                        
                        # 平台统计
                        platform_stats = df['platform'].value_counts()
                        platform_stats.to_excel(writer, sheet_name='统计数据', startrow=10)
                        
                return True
                
        except Exception as e:
            logging.error(f"Excel导出失败: {str(e)}")
            return False
            
    def export_to_json(self):
        """导出为JSON格式"""
        try:
            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query("SELECT * FROM books", conn)
                
                # 转换为字典格式
                data = {
                    'metadata': {
                        'exported_at': datetime.now().isoformat(),
                        'total_records': len(df)
                    },
                    'books': df.to_dict('records')
                }
                
                # 写入JSON文件
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                return True
                
        except Exception as e:
            logging.error(f"JSON导出失败: {str(e)}")
            return False

class ExportPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 导出选项组
        options_group = QGroupBox("导出选项")
        options_layout = QFormLayout()
        
        # 导出格式选择
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON"])
        options_layout.addRow("导出格式:", self.format_combo)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QVBoxLayout()
        
        self.export_raw = QCheckBox("导出原始数据")
        self.export_raw.setChecked(True)
        advanced_layout.addWidget(self.export_raw)
        
        self.export_stats = QCheckBox("导出统计数据")
        self.export_stats.setChecked(True)
        advanced_layout.addWidget(self.export_stats)
        
        self.export_charts = QCheckBox("导出图表")
        self.export_charts.setChecked(True)
        advanced_layout.addWidget(self.export_charts)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("导出数据")
        self.export_button.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel_export)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
    def start_export(self):
        """开始导出数据"""
        export_format = self.format_combo.currentText()
        
        # 获取保存路径
        file_filter = {
            "CSV": "CSV files (*.csv)",
            "Excel": "Excel files (*.xlsx)",
            "JSON": "JSON files (*.json)"
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择保存位置",
            str(Path.home()),
            file_filter[export_format]
        )
        
        if not file_path:
            return
            
        # 准备导出选项
        options = {
            'export_raw': self.export_raw.isChecked(),
            'export_stats': self.export_stats.isChecked(),
            'export_charts': self.export_charts.isChecked()
        }
        
        # 开始导出
        self.export_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.worker = ExportWorker(
            self.db_manager,
            export_format,
            file_path,
            options
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.export_finished)
        self.worker.start()
        
    def cancel_export(self):
        """取消导出"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.export_finished(False, "用户取消导出")
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def export_finished(self, success: bool, message: str):
        """导出完成回调"""
        self.export_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100 if success else 0)
        
        # 显示结果消息
        QMessageBox.information(self, "导出结果", message) 