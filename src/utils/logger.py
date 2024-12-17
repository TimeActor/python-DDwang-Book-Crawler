import logging
from src.config.settings import Settings

class Logger:
    """日志管理工具"""
    
    @staticmethod
    def setup_logger(name: str) -> logging.Logger:
        """
        设置并返回一个命名的日志记录器
        
        Args:
            name: 日志记录器名称
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 确保日志目录存在
        Settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger(name)
        logger.setLevel(Settings.LOG_LEVEL)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            Settings.LOG_FILE, 
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(Settings.LOG_FORMAT))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(Settings.LOG_FORMAT))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger 