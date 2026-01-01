#!/usr/bin/env python3
"""
微信公众号文章爬虫
通过搜狗微信搜索抓取公众号文章
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
import re
from urllib.parse import quote
from article_storage import ArticleStorage


class WeChatScraper:
    """微信公众号文章爬虫类"""

    def __init__(self, storage: ArticleStorage = None):
        """初始化爬虫"""
        self.storage = storage or ArticleStorage()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.base_url = 'https://weixin.sogou.com'

    def search_account(self, account_name: str) -> Optional[str]:
        """
        搜索公众号并获取公众号主页链接

        Args:
            account_name: 公众号名称

        Returns:
            公众号主页URL，如果未找到返回None
        """
        search_url = f"{self.base_url}/weixin?type=1&query={quote(account_name)}"

        try:
            response = self.session.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            # 查找第一个公众号结果
            account_link = soup.select_one('div.txt-box a[uigs*="account_name"]')

            if account_link:
                return account_link.get('href')
            return None

        except Exception as e:
            print(f"搜索公众号失败: {e}")
            return None

    def get_articles_from_sogou(self, account_name: str, max_pages: int = 3) -> List[Dict]:
        """
        从搜狗微信搜索获取公众号文章列表

        Args:
            account_name: 公众号名称
            max_pages: 最大爬取页数

        Returns:
            文章信息列表
        """
        articles = []
        search_url = f"{self.base_url}/weixin?type=2&query={quote(account_name)}"

        for page in range(1, max_pages + 1):
            try:
                url = f"{search_url}&page={page}"
                print(f"正在爬取第 {page} 页...")

                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'lxml')
                news_list = soup.select('div.news-box')

                if not news_list:
                    print(f"第 {page} 页没有找到文章，停止爬取")
                    break

                for news in news_list:
                    try:
                        article = self._parse_article(news, account_name)
                        if article:
                            articles.append(article)
                    except Exception as e:
                        print(f"解析文章失败: {e}")
                        continue

                # 随机延迟，避免被封
                time.sleep(random.uniform(2, 5))

            except Exception as e:
                print(f"爬取第 {page} 页失败: {e}")
                break

        return articles

    def _parse_article(self, news_element, account_name: str) -> Optional[Dict]:
        """
        解析单篇文章信息

        Args:
            news_element: BeautifulSoup元素
            account_name: 公众号名称

        Returns:
            文章信息字典
        """
        try:
            # 标题和链接
            title_elem = news_element.select_one('h3 a')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            url = title_elem.get('href', '')

            # 摘要
            summary_elem = news_element.select_one('p.txt-info')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''

            # 发布时间
            time_elem = news_element.select_one('span.s2')
            publish_time_str = time_elem.get_text(strip=True) if time_elem else ''
            publish_time = self._parse_time(publish_time_str)

            # 封面图片
            cover_elem = news_element.select_one('img')
            cover_image = cover_elem.get('src', '') if cover_elem else ''

            # 作者（从公众号名称中提取）
            author_elem = news_element.select_one('a[uigs*="account_name"]')
            author = author_elem.get_text(strip=True) if author_elem else account_name

            return {
                'title': title,
                'account_name': account_name,
                'author': author,
                'url': url,
                'publish_time': publish_time,
                'content': '',  # 需要进一步爬取文章详情页获取
                'summary': summary,
                'cover_image': cover_image,
                'read_count': 0,
                'like_count': 0,
                'tags': []
            }

        except Exception as e:
            print(f"解析文章元素失败: {e}")
            return None

    def _parse_time(self, time_str: str) -> str:
        """
        解析时间字符串

        Args:
            time_str: 时间字符串，如 "2小时前", "昨天", "2024-01-01"

        Returns:
            ISO格式时间字符串
        """
        now = datetime.now()

        # 匹配"X小时前"
        hour_match = re.search(r'(\d+)小时前', time_str)
        if hour_match:
            hours = int(hour_match.group(1))
            publish_time = now.replace(hour=now.hour - hours)
            return publish_time.strftime('%Y-%m-%d %H:%M:%S')

        # 匹配"昨天"
        if '昨天' in time_str:
            publish_time = now.replace(day=now.day - 1)
            return publish_time.strftime('%Y-%m-%d %H:%M:%S')

        # 匹配"X天前"
        day_match = re.search(r'(\d+)天前', time_str)
        if day_match:
            days = int(day_match.group(1))
            publish_time = now.replace(day=now.day - days)
            return publish_time.strftime('%Y-%m-%d %H:%M:%S')

        # 匹配具体日期 YYYY-MM-DD
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', time_str)
        if date_match:
            return f"{date_match.group(0)} 00:00:00"

        # 默认返回当前时间
        return now.strftime('%Y-%m-%d %H:%M:%S')

    def scrape_and_save(self, account_name: str, max_pages: int = 3) -> int:
        """
        爬取公众号文章并保存到数据库

        Args:
            account_name: 公众号名称
            max_pages: 最大爬取页数

        Returns:
            成功保存的文章数量
        """
        print(f"\n开始爬取公众号: {account_name}")
        articles = self.get_articles_from_sogou(account_name, max_pages)

        saved_count = 0
        for article in articles:
            if self.storage.add_article(article):
                saved_count += 1
                print(f"✓ 保存文章: {article['title']}")
            else:
                print(f"✗ 文章已存在: {article['title']}")

        # 更新公众号信息
        self.storage.update_account(account_name)

        print(f"\n爬取完成: 获取 {len(articles)} 篇文章，保存 {saved_count} 篇新文章")
        return saved_count

    def scrape_multiple_accounts(self, account_names: List[str], max_pages: int = 3):
        """
        批量爬取多个公众号

        Args:
            account_names: 公众号名称列表
            max_pages: 每个公众号的最大爬取页数
        """
        total_saved = 0

        for account_name in account_names:
            try:
                saved = self.scrape_and_save(account_name, max_pages)
                total_saved += saved

                # 每个公众号之间随机延迟
                time.sleep(random.uniform(3, 8))

            except Exception as e:
                print(f"爬取公众号 {account_name} 失败: {e}")
                continue

        print(f"\n\n总计保存 {total_saved} 篇新文章")


if __name__ == "__main__":
    # 测试代码
    scraper = WeChatScraper()

    # 测试爬取单个公众号
    test_account = "人民日报"
    scraper.scrape_and_save(test_account, max_pages=2)

    # 显示统计信息
    stats = scraper.storage.get_statistics()
    print(f"\n数据库统计:")
    print(f"  总文章数: {stats['total_articles']}")
    print(f"  公众号数: {stats['total_accounts']}")
    print(f"  今日新增: {stats['today_count']}")
