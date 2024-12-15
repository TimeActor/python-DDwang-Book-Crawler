import sys
import os

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow
from src.utils.path_manager import PathManager
from PyQt5.QtWidgets import QApplication

def main():
    # 初始化项目目录
    PathManager.initialize_project_directories()
    
    # 启动应用
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 