import sys
from typing import NoReturn
from PyQt5.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.path_manager import PathManager
from src.utils.logger import Logger

# 创建全局日志记录器
logger = Logger.setup_logger(__name__)

def main() -> NoReturn:
    """
    应用程序主入口函数
    初始化必要的目录结构并启动主窗口
    """
    try:
        # 初始化项目目录
        PathManager.initialize_project_directories()
        logger.info("项目目录初始化完成")
        
        # 启动应用
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        logger.info("应用程序启动成功")
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

