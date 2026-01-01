#!/usr/bin/env python3
"""
文章存储模块
使用SQLite数据库存储微信公众号文章
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class ArticleStorage:
    """文章数据库管理类"""

    def __init__(self, db_path: str = "wechat_articles.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """创建数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                account_name TEXT NOT NULL,
                author TEXT,
                url TEXT UNIQUE NOT NULL,
                publish_time TEXT,
                content TEXT,
                summary TEXT,
                cover_image TEXT,
                read_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                scraped_time TEXT NOT NULL,
                tags TEXT,
                is_read BOOLEAN DEFAULT 0
            )
        ''')

        # 创建公众号表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                last_update TEXT,
                article_count INTEGER DEFAULT 0
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_publish_time
            ON articles(publish_time)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_account_name
            ON articles(account_name)
        ''')

        conn.commit()
        conn.close()

    def add_article(self, article: Dict) -> bool:
        """
        添加文章到数据库

        Args:
            article: 文章信息字典，包含title, account_name, url等字段

        Returns:
            bool: 是否成功添加
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO articles (
                    title, account_name, author, url, publish_time,
                    content, summary, cover_image, read_count, like_count,
                    scraped_time, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title'),
                article.get('account_name'),
                article.get('author'),
                article.get('url'),
                article.get('publish_time'),
                article.get('content'),
                article.get('summary'),
                article.get('cover_image'),
                article.get('read_count', 0),
                article.get('like_count', 0),
                datetime.now().isoformat(),
                json.dumps(article.get('tags', []))
            ))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # URL已存在
            return False
        except Exception as e:
            print(f"添加文章失败: {e}")
            return False

    def get_articles_by_date(self, start_date: str, end_date: str = None) -> List[Dict]:
        """
        获取指定日期范围的文章

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)，默认为当天

        Returns:
            文章列表
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM articles
            WHERE publish_time >= ? AND publish_time < date(?, '+1 day')
            ORDER BY publish_time DESC
        ''', (start_date, end_date))

        rows = cursor.fetchall()
        conn.close()

        articles = []
        for row in rows:
            article = dict(row)
            article['tags'] = json.loads(article['tags']) if article['tags'] else []
            articles.append(article)

        return articles

    def get_articles_by_account(self, account_name: str, limit: int = 10) -> List[Dict]:
        """
        获取指定公众号的最新文章

        Args:
            account_name: 公众号名称
            limit: 返回数量限制

        Returns:
            文章列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM articles
            WHERE account_name = ?
            ORDER BY publish_time DESC
            LIMIT ?
        ''', (account_name, limit))

        rows = cursor.fetchall()
        conn.close()

        articles = []
        for row in rows:
            article = dict(row)
            article['tags'] = json.loads(article['tags']) if article['tags'] else []
            articles.append(article)

        return articles

    def update_account(self, name: str, description: str = None):
        """更新公众号信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO accounts (name, description, last_update)
            VALUES (?, ?, ?)
        ''', (name, description, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 总文章数
        cursor.execute('SELECT COUNT(*) FROM articles')
        total_articles = cursor.fetchone()[0]

        # 公众号数
        cursor.execute('SELECT COUNT(DISTINCT account_name) FROM articles')
        total_accounts = cursor.fetchone()[0]

        # 今日新增
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM articles
            WHERE publish_time >= ?
        ''', (today,))
        today_count = cursor.fetchone()[0]

        conn.close()

        return {
            'total_articles': total_articles,
            'total_accounts': total_accounts,
            'today_count': today_count
        }

    def mark_as_read(self, article_id: int):
        """标记文章为已读"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE articles SET is_read = 1 WHERE id = ?
        ''', (article_id,))

        conn.commit()
        conn.close()


if __name__ == "__main__":
    # 测试代码
    storage = ArticleStorage()

    # 添加测试文章
    test_article = {
        'title': '测试文章标题',
        'account_name': '测试公众号',
        'author': '测试作者',
        'url': 'https://example.com/test',
        'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'content': '这是测试内容',
        'summary': '这是摘要',
        'tags': ['测试', 'Python']
    }

    if storage.add_article(test_article):
        print("✓ 文章添加成功")
    else:
        print("✗ 文章已存在或添加失败")

    # 显示统计信息
    stats = storage.get_statistics()
    print(f"\n数据库统计:")
    print(f"  总文章数: {stats['total_articles']}")
    print(f"  公众号数: {stats['total_accounts']}")
    print(f"  今日新增: {stats['today_count']}")
