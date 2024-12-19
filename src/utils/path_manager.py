import os
from pathlib import Path

class PathManager:
    @staticmethod
    def initialize_project_directories():
        """初始化项目所需的所有目录"""
        # 获取项目根目录
        project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 创建必要的目录
        directories = [
            project_root / 'data',
            project_root / 'data/visualizations',
            project_root / 'logs',
            project_root / 'tests'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        return {
            'project_root': project_root,
            'data_dir': project_root / 'data',
            'visualizations_dir': project_root / 'data/visualizations',
            'logs_dir': project_root / 'logs',
            'tests_dir': project_root / 'tests'
        } 