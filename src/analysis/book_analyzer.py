import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import re
from collections import Counter

class BookAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    def _clean_price(self, price: str) -> float:
        """清理价格数据，提取数字"""
        try:
            # 移除货币符号和其他非数字字符
            price = re.findall(r'\d+\.?\d*', price)[0]
            return float(price)
        except:
            return 0.0
            
    def _clean_rating(self, rating: str) -> float:
        """清理评分数据，提取数字"""
        try:
            # 提取评分数字
            rating = re.findall(r'\d+\.?\d*', rating)[0]
            return float(rating)
        except:
            return 0.0

    def _extract_publisher(self, author_info: str) -> str:
        """从作者信息中提取出版社"""
        try:
            # 匹配出版社名称（通常在最后，包含"出版社"字样）
            match = re.search(r'[\u4e00-\u9fa5]+出版社', author_info)
            return match.group() if match else "未知出版社"
        except:
            return "未知出版社"

    def _categorize_book(self, title: str, author_info: str) -> str:
        """根据书名和作者信息对图书进行分类"""
        categories = {
            '小说': r'小说|故事|散文|随笔',
            '教育': r'教育|教材|考试|学习|题库',
            '经管': r'经济|管理|商业|金融|投资',
            '科技': r'科技|计算机|编程|工程|科学',
            '文学': r'文学|诗歌|散文|文集',
            '生活': r'生活|美食|旅游|健康|养生',
            '童书': r'童书|儿童|绘本|少儿',
            '艺术': r'艺术|音乐|绘画|设计',
            '社科': r'社会|科学|哲学|历史|政治'
        }
        
        text = f"{title} {author_info}"
        for category, pattern in categories.items():
            if re.search(pattern, text, re.I):
                return category
        return "其他"

    def get_basic_stats(self) -> Dict:
        """获取基本统计信息"""
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM books", conn)
            
            # 清理数据
            df['price_clean'] = df['price'].apply(self._clean_price)
            df['rating_clean'] = df['rating'].apply(self._clean_rating)
            
            stats = {
                'total_books': len(df),
                'avg_price': df['price_clean'].mean(),
                'max_price': df['price_clean'].max(),
                'min_price': df['price_clean'].min(),
                'avg_rating': df['rating_clean'].mean(),
                'platform_dist': df['platform'].value_counts().to_dict(),
                'date_range': {
                    'start': df['crawl_time'].min(),
                    'end': df['crawl_time'].max()
                }
            }
            
            return stats

    def analyze_price_trends(self) -> pd.DataFrame:
        """分析价格趋势"""
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM books", conn)
            df['price_clean'] = df['price'].apply(self._clean_price)
            df['crawl_date'] = pd.to_datetime(df['crawl_time']).dt.date
            
            price_trends = df.groupby(['crawl_date', 'platform'])['price_clean'].agg([
                'mean', 'min', 'max', 'count'
            ]).reset_index()
            
            return price_trends

    def analyze_publishers(self) -> pd.DataFrame:
        """分析出版社统计"""
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM books", conn)
            df['publisher'] = df['author'].apply(self._extract_publisher)
            
            publisher_stats = df.groupby('publisher').agg({
                'title': 'count',
                'price': lambda x: np.mean([self._clean_price(p) for p in x]),
                'rating': lambda x: np.mean([self._clean_rating(r) for r in x])
            }).reset_index()
            
            publisher_stats.columns = ['publisher', 'book_count', 'avg_price', 'avg_rating']
            return publisher_stats.sort_values('book_count', ascending=False)

    def analyze_categories(self) -> pd.DataFrame:
        """分析图书分类统计"""
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM books", conn)
            df['category'] = df.apply(lambda x: self._categorize_book(x['title'], x['author']), axis=1)
            
            category_stats = df.groupby('category').agg({
                'title': 'count',
                'price': lambda x: np.mean([self._clean_price(p) for p in x]),
                'rating': lambda x: np.mean([self._clean_rating(r) for r in x])
            }).reset_index()
            
            category_stats.columns = ['category', 'book_count', 'avg_price', 'avg_rating']
            return category_stats.sort_values('book_count', ascending=False)

    def analyze_keywords(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """分析书名关键词"""
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT title FROM books", conn)
            
            # 分词并统计
            words = []
            for title in df['title']:
                # 简单的分词（可以使用更复杂的分词库如jieba）
                words.extend(re.findall(r'[\u4e00-\u9fa5]+', title))
            
            # 过滤停用词
            stop_words = {'的', '了', '和', '与', '或', '之', '等', '及', '上', '中', '下'}
            words = [w for w in words if len(w) > 1 and w not in stop_words]
            
            # 统计词频
            word_counts = Counter(words).most_common(top_n)
            return word_counts

    def analyze_price_segments(self) -> Dict[str, int]:
        """分析价格区间分布"""
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT price FROM books", conn)
            df['price_clean'] = df['price'].apply(self._clean_price)
            
            bins = [0, 30, 50, 100, 200, float('inf')]
            labels = ['0-30元', '30-50元', '50-100元', '100-200元', '200元以上']
            df['price_range'] = pd.cut(df['price_clean'], bins=bins, labels=labels)
            
            distribution = df['price_range'].value_counts().to_dict()
            return distribution

    def generate_summary_report(self) -> Dict:
        """生成完整的分析报告"""
        try:
            # 基本统计
            basic_stats = self.get_basic_stats()
            
            # 价格趋势
            price_trends = self.analyze_price_trends()
            
            # 出版社分析
            publisher_stats = self.analyze_publishers()
            
            # 分类分析
            category_stats = self.analyze_categories()
            
            # 关键词分析
            keyword_stats = self.analyze_keywords()
            
            report = {
                'basic_stats': basic_stats,
                'price_trends': price_trends.to_dict('records'),
                'publisher_stats': publisher_stats.head(10).to_dict('records'),
                'category_stats': category_stats.to_dict('records'),
                'keyword_stats': dict(keyword_stats),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成报告时出错: {str(e)}")
            return {} 