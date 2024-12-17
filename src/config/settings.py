from pathlib import Path

class Settings:
    """全局设置类"""
    # 项目路径配置
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    SRC_DIR = PROJECT_ROOT / "src"
    LOGS_DIR = PROJECT_ROOT / "logs"
    DATA_DIR = PROJECT_ROOT / "data"
    CACHE_DIR = DATA_DIR / "cache"

    # 应用配置
    APP_NAME = "Your App Name"
    APP_VERSION = "1.0.0"

    # 日志配置
    LOG_FILE = LOGS_DIR / "app.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL = "INFO" 