import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import List, Dict
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.path_manager import PathManager

class BookCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.logger = logging.getLogger(__name__)
        self.paths = PathManager.initialize_project_directories()
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志"""
        log_file = self.paths['logs_dir'] / 'crawler.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def _random_sleep(self):
        """随机延时，避免被反爬"""
        time.sleep(random.uniform(1, 3))

    def crawl_dangdang(self, keywords: str = None, pages: int = 1, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        爬取当当网图书数据
        
        Args:
            keywords: 搜索关键词
            pages: 爬取页数
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            List[Dict]: 图书数据列表
        """
        books = []
        # 如果有关键词，使用搜索URL，否则使用畅销榜URL
        if keywords:
            base_url = "http://search.dangdang.com/"
        else:
            base_url = "http://bang.dangdang.com/books/bestsellers"
        
        try:
            for page in range(1, pages + 1):
                self._random_sleep()
                
                if keywords:
                    url = f"{base_url}?key={keywords}&act=input&page_index={page}"
                else:
                    url = f"{base_url}/01.00.00.00.00.00-month-2023-0-1-{page}"
                    
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 根据不同页面使用不同的选择器
                items = soup.select('.bang_list li' if not keywords else '#search_nature_rg ul.bigimg li')
                
                for item in items:
                    try:
                        if keywords:
                            # 搜索页面的数据提取
                            book = {
                                'title': item.select_one('.name a').text.strip(),
                                'author': item.select_one('.search_book_author span').text.strip(),
                                'price': item.select_one('.search_now_price').text.strip(),
                                'rating': "暂无评分",  # 搜索页面可能没有评分
                                'url': item.select_one('.name a')['href'],
                                'platform': '当当网',
                                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        else:
                            # 畅销榜页面的数据提取
                            book = {
                                'title': item.select_one('.name a').text.strip(),
                                'author': item.select_one('.publisher_info').text.strip(),
                                'price': item.select_one('.price .price_n').text.strip(),
                                'rating': item.select_one('.star').text.strip() if item.select_one('.star') else "暂无评分",
                                'url': item.select_one('.name a')['href'],
                                'platform': '当当网',
                                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        
                        # 检查是否在日期范围内
                        if start_date and end_date:
                            book_time = datetime.strptime(book['crawl_time'], '%Y-%m-%d %H:%M:%S')
                            start = datetime.strptime(start_date, '%Y-%m-%d')
                            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                            
                            if start <= book_time <= end:
                                books.append(book)
                                self.logger.info(f"成功爬取图书: {book['title']}")
                        else:
                            books.append(book)
                            self.logger.info(f"成功爬取图书: {book['title']}")
                        
                    except Exception as e:
                        self.logger.error(f"解析图书数据时出错: {str(e)}")
                        continue
                
                self.logger.info(f"已完成第{page}页数据爬取，当前获取{len(books)}条数据")
                
            return books
                
        except Exception as e:
            self.logger.error(f"爬取过程中出现错误: {str(e)}")
            return books