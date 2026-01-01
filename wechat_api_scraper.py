#!/usr/bin/env python3
"""
微信公众号 API 爬虫
通过微信公众号后台 API 直接获取文章列表
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from article_storage import ArticleStorage
from urllib.parse import quote


class WeChatAPIScraper:
    """微信公众号 API 爬虫（使用后台接口）"""

    def __init__(self, token: str, cookie: str, storage: ArticleStorage = None):
        """
        初始化爬虫

        Args:
            token: 微信后台认证 token
            cookie: 完整的 Cookie 字符串
            storage: 文章存储实例
        """
        self.token = token
        self.cookie = cookie
        self.storage = storage or ArticleStorage()
        self.base_url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"

        # 公众号 fakeid 映射
        self.fakeid_mapping = {
            '光储星球': 'MzkyNzYxNzYwNg=='
        }

    def get_articles_from_api(
        self,
        account_name: str,
        days: int = 7,
        max_articles: int = 100
    ) -> List[Dict]:
        """
        从微信后台 API 获取文章列表

        Args:
            account_name: 公众号名称
            days: 时间范围（天数）
            max_articles: 最多获取文章数量

        Returns:
            文章列表
        """
        # 获取 fakeid
        fakeid = self.fakeid_mapping.get(account_name)
        if not fakeid:
            print(f"错误: 未找到公众号 {account_name} 的 fakeid")
            print(f"当前支持的公众号: {', '.join(self.fakeid_mapping.keys())}")
            return []

        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        print(f"\n{'='*60}")
        print(f"开始爬取公众号: {account_name}")
        print(f"爬取方式: 微信后台 API")
        print(f"时间范围: {start_time.strftime('%Y-%m-%d')} 至 {end_time.strftime('%Y-%m-%d')}")
        print(f"{'='*60}\n")

        articles = []
        begin = 0
        count = 20  # 每次请求 20 篇

        while len(articles) < max_articles:
            print(f"正在获取第 {begin + 1} - {begin + count} 篇文章...")

            # 构建请求参数
            params = {
                'sub': 'list',
                'search_field': 'null',
                'begin': begin,
                'count': count,
                'query': '',
                'fakeid': fakeid,
                'type': '101_1',
                'free_publish_type': '1',
                'sub_action': 'list_ex',
                'token': self.token,
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1'
            }

            # 构建请求头
            headers = {
                'Cookie': self.cookie,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg',
                'Accept': '*/*'
            }

            try:
                # 发送请求
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=30
                )

                if response.status_code != 200:
                    print(f"✗ 请求失败: HTTP {response.status_code}")
                    break

                # 解析响应
                data = response.json()

                if data.get('base_resp', {}).get('ret') != 0:
                    print(f"✗ API 返回错误: {data.get('base_resp', {}).get('err_msg')}")
                    break

                # 解析文章列表
                publish_page = json.loads(data.get('publish_page', '{}'))
                total_count = publish_page.get('total_count', 0)
                publish_list = publish_page.get('publish_list', [])

                if not publish_list:
                    print("已获取所有文章")
                    break

                # 处理每条发布记录
                found_old_article = False
                for publish_item in publish_list:
                    publish_info = json.loads(publish_item.get('publish_info', '{}'))
                    appmsgex_list = publish_info.get('appmsgex', [])

                    # 处理每篇文章
                    for appmsg in appmsgex_list:
                        # 提取文章信息
                        article = self._parse_article(appmsg, account_name)
                        if not article:
                            continue

                        # 时间过滤
                        article_time = datetime.strptime(
                            article['publish_time'],
                            '%Y-%m-%d %H:%M:%S'
                        )

                        if start_time <= article_time <= end_time:
                            articles.append(article)
                            print(f"  ✓ [{article_time.strftime('%m-%d %H:%M')}] {article['title'][:50]}...")
                        elif article_time < start_time:
                            print(f"  ✗ 文章太老: {article['title'][:40]}... ({article_time.strftime('%Y-%m-%d')})")
                            found_old_article = True

                        # 检查是否已达到最大数量
                        if len(articles) >= max_articles:
                            break

                    if found_old_article or len(articles) >= max_articles:
                        break

                # 如果遇到旧文章或达到最大数量，停止
                if found_old_article or len(articles) >= max_articles:
                    break

                # 更新偏移量
                begin += count

                # 避免请求过快
                time.sleep(1)

            except requests.RequestException as e:
                print(f"✗ 网络请求错误: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"✗ JSON 解析错误: {e}")
                break
            except Exception as e:
                print(f"✗ 未知错误: {e}")
                break

        print(f"\n爬取完成: 共获取 {len(articles)} 篇文章\n")
        return articles

    def _parse_article(self, appmsg: Dict, account_name: str) -> Optional[Dict]:
        """
        解析单篇文章信息

        Args:
            appmsg: API 返回的文章数据
            account_name: 公众号名称

        Returns:
            标准化的文章字典
        """
        try:
            # 提取基本信息
            title = appmsg.get('title', '').strip()
            link = appmsg.get('link', '').strip()
            digest = appmsg.get('digest', '').strip()
            update_time = appmsg.get('update_time', 0)

            if not title or not link:
                return None

            # 转换时间戳
            publish_time = datetime.fromtimestamp(update_time)

            return {
                'title': title,
                'url': link,
                'publish_time': publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                'account': account_name,
                'summary': digest,  # API 已提供摘要
                'author': appmsg.get('author_name', account_name)
            }

        except Exception as e:
            print(f"  ✗ 解析文章失败: {e}")
            return None

    def scrape_and_save(self, account_name: str, days: int = 7) -> int:
        """
        爬取并保存文章

        Args:
            account_name: 公众号名称
            days: 时间范围（天数）

        Returns:
            保存的新文章数量
        """
        # 获取文章
        articles = self.get_articles_from_api(account_name, days)

        if not articles:
            print("没有获取到文章")
            return 0

        # 保存到数据库
        print("保存文章到数据库...\n")
        saved_count = 0

        for article in articles:
            try:
                success = self.storage.save_article(
                    title=article['title'],
                    url=article['url'],
                    publish_time=article['publish_time'],
                    account=article['account'],
                    summary=article['summary'],
                    author=article.get('author', article['account'])
                )

                if success:
                    saved_count += 1
                    print(f"  ✓ 保存: {article['title'][:50]}...")
                else:
                    print(f"  ✗ 已存在: {article['title'][:50]}...")

            except Exception as e:
                print(f"  ✗ 保存失败: {article['title'][:40]}... - {e}")

        print(f"\n{'='*60}")
        print(f"爬取完成: 获取 {len(articles)} 篇文章，保存 {saved_count} 篇新文章")
        print(f"{'='*60}\n")

        return saved_count


# 配置文件加载
def load_api_config(filepath: str = 'wechat_api_config.txt') -> Optional[Dict[str, str]]:
    """从配置文件加载 API 配置"""
    try:
        config = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

        # 验证必需字段
        if 'token' not in config or 'cookie' not in config:
            print(f"⚠️  配置文件缺少必需字段: token 或 cookie")
            return None

        return config

    except FileNotFoundError:
        print(f"⚠️  未找到配置文件: {filepath}")
        print(f"请创建配置文件，格式如下:")
        print(f"token=你的token")
        print(f"cookie=你的完整cookie字符串")
        return None
    except Exception as e:
        print(f"⚠️  读取配置文件失败: {e}")
        return None


# 同步包装函数
def scrape_wechat_api(account_name: str, days: int = 7) -> int:
    """
    同步接口：使用 API 爬取微信公众号

    Args:
        account_name: 公众号名称
        days: 时间范围（天数）

    Returns:
        保存的新文章数量
    """
    # 加载配置
    config = load_api_config()
    if not config:
        return 0

    # 创建爬虫实例
    scraper = WeChatAPIScraper(
        token=config['token'],
        cookie=config['cookie']
    )

    # 爬取并保存
    return scraper.scrape_and_save(account_name, days)


if __name__ == "__main__":
    # 测试代码
    print("测试微信 API 爬虫...")
    count = scrape_wechat_api("光储星球", days=7)
    print(f"\n成功保存 {count} 篇新文章")
