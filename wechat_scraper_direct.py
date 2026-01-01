#!/usr/bin/env python3
"""
微信公众号直接爬虫（基于 Playwright）
通过公众号 biz 参数直接访问历史消息页面
"""

import asyncio
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page
from article_storage import ArticleStorage


class WeChatDirectScraper:
    """微信公众号直接爬虫（使用 Playwright）"""

    def __init__(self, storage: ArticleStorage = None):
        """初始化爬虫"""
        self.storage = storage or ArticleStorage()
        self.biz_mapping = {
            '光储星球': 'MzkyNzYxNzYwNg=='
        }

    async def get_articles_from_wechat(self, account_name: str, days: int = 7) -> List[Dict]:
        """
        从微信公众号历史消息页面获取文章（实时、完整）

        Args:
            account_name: 公众号名称
            days: 爬取最近多少天的文章（默认7天）

        Returns:
            文章信息列表
        """
        # 获取 biz 参数
        biz = self.biz_mapping.get(account_name)
        if not biz:
            print(f"错误: 未找到公众号 {account_name} 的 biz 参数")
            print(f"当前支持的公众号: {', '.join(self.biz_mapping.keys())}")
            return []

        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        print(f"\n{'='*60}")
        print(f"开始爬取公众号: {account_name}")
        print(f"爬取方式: 直接访问微信历史消息页面")
        print(f"时间范围: {start_time.strftime('%Y-%m-%d')} 至 {end_time.strftime('%Y-%m-%d')}")
        print(f"{'='*60}\n")

        articles = []

        async with async_playwright() as p:
            # 启动浏览器（无头模式）
            browser = await p.chromium.launch(
                headless=True,  # 设为 False 可以看到浏览器运行过程
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            # 创建上下文（模拟手机微信）
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0',
                viewport={'width': 375, 'height': 812},
                locale='zh-CN'
            )

            page = await context.new_page()

            try:
                # 构建历史消息 URL
                # 注意：这个 URL 可能需要调整参数
                history_url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124"

                print(f"正在访问历史消息页面...")
                print(f"URL: {history_url}")
                await page.goto(history_url, timeout=30000, wait_until='domcontentloaded')

                # 保存页面截图用于调试
                await page.screenshot(path='debug_page.png')
                print(f"✓ 页面截图已保存: debug_page.png")

                # 保存页面 HTML 用于调试
                html_content = await page.content()
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✓ 页面 HTML 已保存: debug_page.html")

                # 等待内容加载
                await asyncio.sleep(3)

                # 滚动加载更多文章
                print(f"正在加载文章列表...")
                articles = await self._scroll_and_collect(page, start_time, end_time, account_name)

                print(f"\n爬取完成: 共获取 {len(articles)} 篇文章")

            except Exception as e:
                print(f"爬取失败: {e}")
                # 保存截图用于调试
                await page.screenshot(path="error_screenshot.png")
                print(f"已保存错误截图到 error_screenshot.png")

            finally:
                await browser.close()

        return articles

    async def _scroll_and_collect(
        self,
        page: Page,
        start_time: datetime,
        end_time: datetime,
        account_name: str
    ) -> List[Dict]:
        """滚动页面并收集文章"""

        articles = []
        consecutive_old = 0
        max_consecutive_old = 5

        # 尝试多种选择器（微信页面结构可能变化）
        selectors = [
            '.weui_media_box',
            '.album__list-item',
            'div[data-title]',
            '.js_album_item'
        ]

        for scroll_count in range(30):  # 最多滚动30次
            print(f"正在滚动加载... ({scroll_count + 1}/30)")

            # 滚动到底部
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)  # 等待加载

            # 尝试找到文章元素
            article_elements = None
            for selector in selectors:
                try:
                    article_elements = await page.query_selector_all(selector)
                    if article_elements and len(article_elements) > 0:
                        print(f"  找到 {len(article_elements)} 个文章元素 (使用选择器: {selector})")
                        break
                except:
                    continue

            if not article_elements or len(article_elements) == 0:
                print(f"  未找到文章元素，尝试其他方式...")
                continue

            # 解析文章
            for elem in article_elements:
                try:
                    article = await self._parse_wechat_article(elem, account_name)
                    if not article:
                        continue

                    # 检查是否已存在（避免重复）
                    if any(a['url'] == article['url'] for a in articles):
                        continue

                    # 时间过滤
                    article_time = datetime.strptime(article['publish_time'], '%Y-%m-%d %H:%M:%S')

                    if start_time <= article_time <= end_time:
                        articles.append(article)
                        print(f"  ✓ [{article_time.strftime('%m-%d %H:%M')}] {article['title'][:40]}...")
                        consecutive_old = 0
                    elif article_time < start_time:
                        consecutive_old += 1
                        print(f"  ✗ 文章太老: {article['title'][:40]}... ({article_time.strftime('%Y-%m-%d')})")

                        if consecutive_old >= max_consecutive_old:
                            print(f"\n已连续遇到 {consecutive_old} 篇超出时间范围的文章，停止爬取")
                            return articles

                except Exception as e:
                    print(f"  ✗ 解析文章失败: {e}")
                    continue

            # 检查是否到底
            is_bottom = await page.evaluate('''
                () => {
                    return window.scrollY + window.innerHeight >= document.body.scrollHeight - 10;
                }
            ''')

            if is_bottom and scroll_count > 5:
                print(f"\n已到达页面底部")
                break

        return articles

    async def _parse_wechat_article(self, element, account_name: str) -> Optional[Dict]:
        """解析微信文章元素"""

        try:
            # 提取标题
            title = None
            title_selectors = ['[data-title]', '.weui_media_title', 'h4', '.album__item-title']
            for selector in title_selectors:
                try:
                    title_elem = await element.query_selector(selector)
                    if title_elem:
                        title = await title_elem.get_attribute('data-title') or await title_elem.inner_text()
                        if title:
                            title = title.strip()
                            break
                except:
                    continue

            if not title:
                return None

            # 提取链接
            url = None
            try:
                link_elem = await element.query_selector('a')
                if link_elem:
                    url = await link_elem.get_attribute('href')
                    if url and not url.startswith('http'):
                        url = 'https://mp.weixin.qq.com' + url
            except:
                pass

            # 提取时间
            publish_time = None
            time_selectors = ['.weui_media_extra_info', '[data-time]', '.album__item-time', 'span.time']
            for selector in time_selectors:
                try:
                    time_elem = await element.query_selector(selector)
                    if time_elem:
                        time_str = await time_elem.get_attribute('data-time') or await time_elem.inner_text()
                        if time_str:
                            publish_time = self._parse_time(time_str.strip())
                            if publish_time:
                                break
                except:
                    continue

            if not publish_time:
                # 默认当前时间
                publish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 提取摘要（如果有）
            summary = ''
            try:
                summary_elem = await element.query_selector('.weui_media_desc, .album__item-desc')
                if summary_elem:
                    summary = await summary_elem.inner_text()
                    summary = summary.strip() if summary else ''
            except:
                pass

            return {
                'title': title,
                'url': url or '',
                'publish_time': publish_time,
                'summary': summary,
                'account_name': account_name,
                'author': account_name,
                'cover_image': '',
                'read_count': 0,
                'like_count': 0,
                'tags': []
            }

        except Exception as e:
            print(f"解析文章元素失败: {e}")
            return None

    def _parse_time(self, time_str: str) -> Optional[str]:
        """解析时间字符串"""
        now = datetime.now()

        try:
            # Unix 时间戳（秒）
            if time_str.isdigit():
                timestamp = int(time_str)
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime('%Y-%m-%d %H:%M:%S')

            # "X小时前"
            hour_match = re.search(r'(\d+)\s*小时前', time_str)
            if hour_match:
                hours = int(hour_match.group(1))
                dt = now - timedelta(hours=hours)
                return dt.strftime('%Y-%m-%d %H:%M:%S')

            # "昨天"
            if '昨天' in time_str:
                dt = now - timedelta(days=1)
                return dt.strftime('%Y-%m-%d %H:%M:%S')

            # "X天前"
            day_match = re.search(r'(\d+)\s*天前', time_str)
            if day_match:
                days = int(day_match.group(1))
                dt = now - timedelta(days=days)
                return dt.strftime('%Y-%m-%d %H:%M:%S')

            # "YYYY-MM-DD"
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', time_str)
            if date_match:
                return f"{date_match.group(0)} 00:00:00"

            # "MM-DD"
            date_match = re.search(r'(\d{1,2})-(\d{1,2})', time_str)
            if date_match:
                month = int(date_match.group(1))
                day = int(date_match.group(2))
                year = now.year
                if month > now.month:
                    year -= 1
                return f"{year}-{month:02d}-{day:02d} 00:00:00"

        except Exception as e:
            print(f"时间解析失败: {time_str} - {e}")

        # 默认返回当前时间
        return now.strftime('%Y-%m-%d %H:%M:%S')

    async def scrape_and_save(self, account_name: str, days: int = 7) -> int:
        """爬取并保存到数据库"""

        articles = await self.get_articles_from_wechat(account_name, days)

        print(f"\n保存文章到数据库...")
        saved_count = 0
        for article in articles:
            if self.storage.add_article(article):
                saved_count += 1
                print(f"  ✓ 保存: {article['title'][:50]}...")
            else:
                print(f"  ✗ 已存在: {article['title'][:50]}...")

        self.storage.update_account(account_name)

        print(f"\n{'='*60}")
        print(f"爬取完成: 获取 {len(articles)} 篇文章，保存 {saved_count} 篇新文章")
        print(f"{'='*60}\n")

        return saved_count


# 同步包装函数
def scrape_wechat_direct(account_name: str, days: int = 7) -> int:
    """同步接口：爬取微信公众号"""
    scraper = WeChatDirectScraper()
    return asyncio.run(scraper.scrape_and_save(account_name, days))


if __name__ == "__main__":
    # 测试代码
    print("测试直接爬取微信公众号...")
    count = scrape_wechat_direct("光储星球", days=7)
    print(f"\n成功保存 {count} 篇新文章")
