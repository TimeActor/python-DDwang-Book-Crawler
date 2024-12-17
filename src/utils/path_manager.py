from src.config.settings import Settings

class PathManager:
    """路径管理工具"""
    
    @classmethod
    def initialize_project_directories(cls) -> None:
        """初始化项目所需的目录结构"""
        # 创建所有必要的目录
        for directory in [
            Settings.LOGS_DIR,
            Settings.DATA_DIR,
            Settings.CACHE_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)