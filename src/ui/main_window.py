from PyQt5.QtWidgets import QMainWindow
from src.utils.logger import Logger

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.logger = Logger.setup_logger(__name__)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Your App")
        self.setGeometry(100, 100, 800, 600)
        self.logger.debug("主窗口UI初始化完成") 