# 当当网图书畅销榜数据分析系统

## 项目简介
本项目是一个基于Python的当当网图书畅销榜数据采集与分析系统。系统可以从当当网采集图书销售数据，进行数据清洗和分析，并以可视化方式展示分析结果。用户可以通过图形界面轻松操作，获取图书市场的各项统计数据。

## 功能特性
1. 数据采集
   - 支持从当当网、京东等平台采集图书数据
   - 可设置采集时间范围和页数
   - 支持按关键词搜索采集
   - 实时显示采集进度
   - 自动处理反爬限制

2. 数据存储
   - 支持SQLite数据库存储
   - 支持导出为CSV、Excel、JSON格式
   - 自动备份功能
   - 数据去重和更新

3. 数据分析
   - 销量排行榜分析
   - 价格区间分布分析
   - 出版社统计分析
   - 图书分类分布分析
   - 评分与销量关系分析

4. 数据可视化
   - 柱状图展示销量TOP10
   - 饼图展示分类占比
   - 折线图展示价格趋势
   - 散点图展示评分与销量关系
   - 支持图表导出

## 技术架构
- 爬虫框架���requests + BeautifulSoup4
- 数据处理：pandas + numpy
- 数据可视化：matplotlib + seaborn
- 数据存储：SQLite
- 用户界面：PyQt5

## 项目结构
book_analysis/
├── src/ # 源代码目录
│ ├── crawler/ # 爬虫模块
│ │ ├── init.py
│ │ └── book_crawler.py
│ ├── database/ # 数据库模块
│ │ ├── init.py
│ │ └── db_manager.py
│ ├── analysis/ # 数据分析模块
│ │ ├── init.py
│ │ └── book_analyzer.py
│ ├── visualization/ # 可视化模块
│ │ ├── init.py
│ │ └── data_visualizer.py
│ ├── ui/ # 用户界面模块
│ │ ├── init.py
│ │ ├── main_window.py
│ │ ├── crawler_panel.py
│ │ ├── analysis_panel.py
│ │ └── export_panel.py
│ └── main.py # 程序入口
├── data/ # 数据目录
│ ├── books.db # SQLite数据库文件
│ └── visualizations/ # 可视化图表目录
│ ├── sales_ranking.png
│ ├── price_distribution.png
│ ├── publisher_stats.png
│ └── category_distribution.png
├── logs/ # 日志目录
│ ├── app.log # 应用程序日志
│ └── crawler.log # 爬虫日志
├── tests/ # 测试目录
│ ├── init.py
│ ├── test_crawler.py
│ ├── test_analyzer.py
│ └── test_visualizer.py
├── requirements.txt # 项目依赖
├── LICENSE # 许可证文件
└── README.md # 项目说明文档

## 安装和使用流程

### 1. 环境准备
1. 安装Python环境
   - 下载并安装Python 3.8或更高版本：https://www.python.org/downloads/
   - 确保Python和pip已添加到系统环境变量

2. 安装依赖包
   ```bash
   # Windows系统
   # 方式1：单独安装每个包
   pip install requests beautifulsoup4 pandas numpy matplotlib seaborn PyQt5 python-dateutil openpyxl

   # 方式2：使用requirements.txt（如果遇到编码错误，请使用以下命令）
   pip install -r requirements.txt --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple

   # Linux/Mac系统
   pip3 install -r requirements.txt
   ```

3. 验证安装
   ```bash
   # 验证所有包是否安装成功
   python -c "import requests, bs4, pandas, numpy, matplotlib, seaborn, PyQt5, openpyxl"
   ```

### 2. 程序使用流程
1. 启动程序
   ```bash
   cd book_analysis  # 进入项目目录
   python src/main.py
   ```

2. 数据采集流程
   - 打开程序后，默认显示"数据采集"标签页
   - 选择要采集的平台（当当网/京东）
   - 可选：输入搜索关键词
   - 设置要采集的页数（建议先少量测试）
   - 点击"开始采集"按钮
   - 等待采集完成，可在日志区域查看进度

3. 数据分析流程
   - 切换到"数据分析"标签页
   - 选择分析类型：
     * 销量排行榜
     * 价格分布
     * 出版社统计
     * 分类分布
     * 评分价格关系
   - 可选：选择特定平台的数据
   - 点击"开始分析"按钮
   - 查看生成的图表和统计结果

4. 数据导出流程
   - 切换到"数据导出"标签页
   - 选择导出格��（CSV/Excel/JSON）
   - 选择导出选项：
     * 原始数据
     * 统计数据
     * 图表
   - 点击"导出数据"按钮
   - 选择保存位置
   - 等待导出完成

### 3. 注意事项
1. 首次运行
   - 确保所有依赖包安装成功
   - 程序会自动创建必要的目录和数据库
   - 建议先采集少量数据测试

2. 数据采集
   - 遵守网站robots协议
   - 建议采集间隔不少于1��
   - 避免频繁大量请求

3. 数据管理
   - 定期备份data/books.db数据库
   - 及时清理不需要的图表文件
   - 检查logs目录下的日志信息

### 4. 常见问题解决
1. 依赖安装失败
   - 确保pip是最新版本：`pip install --upgrade pip`
   - 尝试使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

2. 程序启动失败
   - 检查Python版本是否满足要求
   - 确认所有依赖包安装成功
   - 查看logs/app.log中的错误信息

3. 采集数据失败
   - 检查网络连接
   - 确认目标网站是否可访问
   - 查看logs/crawler.log中的错误信息

## 开发计划
- [x] 项目初始化
- [x] 爬虫模块开发
- [x] 数据库模块开发
- [x] 数据分析模块开发
- [x] 可视化模块开发
- [x] 用户界面开发
- [ ] 系统测试与优化
- [ ] 添加更���数据源
- [ ] 优化分析算法
- [ ] 增加导出格式

## 问题反馈
如果您在使用过程中遇到任何问题，或有任何建议，请通过以下方式反馈：
1. 提交Issue
2. 发送邮件
3. 在线讨论

## 许可证
本项目采用MIT许可证，详见LICENSE文件。