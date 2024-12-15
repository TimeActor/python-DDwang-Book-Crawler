from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QSpinBox, QComboBox, QPushButton,
                           QProgressBar, QTextEdit, QDateEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
from src.crawler.book_crawler import BookCrawler
from src.database.db_manager import DatabaseManager

class CrawlerWorker(QThread):
    """爬虫工作线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, crawler, keywords, pages, start_date, end_date):
        super().__init__()
        self.crawler = crawler
        self.keywords = keywords
        self.pages = pages
        self.start_date = start_date
        self.end_date = end_date
        
    def run(self):
        try:
            books = self.crawler.crawl_dangdang(self.keywords, self.pages, self.start_date, self.end_date)
            
            # 保存到数据库
            db_manager = DatabaseManager()
            success = db_manager.save_books(books)
            
            self.finished.emit(success, f"成功采集{len(books)}条数据" if success else "数据采集失败")
        except Exception as e:
            self.finished.emit(False, f"发生错误: {str(e)}")

class CrawlerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.crawler = BookCrawler()
        
    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 参数设置区域
        param_layout = QHBoxLayout()
        
        # 关键词输入
        param_layout.addWidget(QLabel("关键词:"))
        self.keyword_edit = QLineEdit()
        param_layout.addWidget(self.keyword_edit)
        
        # 页数设置
        param_layout.addWidget(QLabel("页数:"))
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 100)
        self.page_spin.setValue(1)
        param_layout.addWidget(self.page_spin)
        
        layout.addLayout(param_layout)
        
        # 日期选择区域
        date_layout = QHBoxLayout()
        
        # 开始日期
        date_layout.addWidget(QLabel("开始日期:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))  # 默认7天前
        date_layout.addWidget(self.start_date)
        
        # 结束日期
        date_layout.addWidget(QLabel("结束日期:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())  # 默认今天
        date_layout.addWidget(self.end_date)
        
        layout.addLayout(date_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始采集")
        self.start_button.clicked.connect(self.start_crawling)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止采集")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_crawling)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
    def start_crawling(self):
        """开始爬取数据"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # 获取日期范围
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
        # 创建并启动工作线程
        self.worker = CrawlerWorker(
            self.crawler,
            self.keyword_edit.text(),
            self.page_spin.value(),
            start_date,
            end_date
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.crawling_finished)
        self.worker.start()
        
        self.log_text.append("开始采集数据...")
        
    def stop_crawling(self):
        """停止爬取数据"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.crawling_finished(False, "用户停止采集")
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def crawling_finished(self, success: bool, message: str):
        """爬虫完成回调"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100 if success else 0)
        self.log_text.append(message) 