import sqlite3
import pandas as pd
from typing import List, Dict
import logging
from datetime import datetime
from src.utils.path_manager import PathManager

class DatabaseManager:
    def __init__(self):
        paths = PathManager.initialize_project_directories()
        self.db_path = paths['data_dir'] / 'books.db'
        self.logger = logging.getLogger(__name__)
        self.init_database()
        
    def init_database(self):
        """初始化数据库，创建必要的表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建图书表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    price TEXT,
                    rating TEXT,
                    url TEXT,
                    platform TEXT,
                    crawl_time DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON books(title)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON books(platform)')
                
                conn.commit()
                self.logger.info("数据库初始化成功")
                
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {str(e)}")
            
    def save_books(self, books: List[Dict]) -> bool:
        """
        保存图书数据到数据库
        
        Args:
            books: 图书数据列表
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for book in books:
                    cursor.execute('''
                    INSERT INTO books (title, author, price, rating, url, platform, crawl_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        book['title'],
                        book['author'],
                        book['price'],
                        book['rating'],
                        book['url'],
                        book['platform'],
                        book['crawl_time']
                    ))
                
                conn.commit()
                self.logger.info(f"成功保存 {len(books)} 条图书数据")
                return True
                
        except Exception as e:
            self.logger.error(f"保存图书数据失败: {str(e)}")
            return False
            
    def export_to_csv(self, output_path: str) -> bool:
        """
        导出数据库数据到CSV文件
        
        Args:
            output_path: CSV文件保存路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM books", conn)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                self.logger.info(f"成功导出数据到 {output_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"导出CSV文件失败: {str(e)}")
            return False 

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)