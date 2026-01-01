#!/usr/bin/env python3
"""
每日文章摘要生成器
将每日爬取的文章整理成Markdown格式的文档
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict
from article_storage import ArticleStorage
from collections import defaultdict


class DigestGenerator:
    """每日文章摘要生成器"""

    def __init__(self, storage: ArticleStorage = None, output_dir: str = "digests"):
        """
        初始化生成器

        Args:
            storage: 文章存储实例
            output_dir: 输出目录
        """
        self.storage = storage or ArticleStorage()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_daily_digest(self, date: str = None) -> str:
        """
        生成指定日期的每日摘要

        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为今天

        Returns:
            生成的文件路径
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # 获取当天文章
        articles = self.storage.get_articles_by_date(date, date)

        if not articles:
            print(f"⚠ {date} 没有找到文章")
            return None

        # 按公众号分组
        grouped = self._group_by_account(articles)

        # 生成Markdown内容
        content = self._generate_markdown(date, grouped, articles)

        # 保存文件
        filename = f"digest_{date}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ 每日摘要已生成: {filepath}")
        return filepath

    def generate_weekly_digest(self, start_date: str = None) -> str:
        """
        生成周摘要（最近7天）

        Args:
            start_date: 开始日期 (YYYY-MM-DD)，默认为7天前

        Returns:
            生成的文件路径
        """
        if start_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
        else:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = start_date_obj + timedelta(days=7)
            start_date_str = start_date
            end_date_str = end_date_obj.strftime('%Y-%m-%d')

        # 获取周内所有文章
        articles = self.storage.get_articles_by_date(start_date_str, end_date_str)

        if not articles:
            print(f"⚠ {start_date_str} 到 {end_date_str} 没有找到文章")
            return None

        # 按日期分组
        grouped_by_date = self._group_by_date(articles)

        # 生成Markdown内容
        content = self._generate_weekly_markdown(start_date_str, end_date_str, grouped_by_date)

        # 保存文件
        filename = f"weekly_digest_{start_date_str}_to_{end_date_str}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ 周摘要已生成: {filepath}")
        return filepath

    def _group_by_account(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """按公众号分组文章"""
        grouped = defaultdict(list)
        for article in articles:
            grouped[article['account_name']].append(article)
        return dict(grouped)

    def _group_by_date(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """按日期分组文章"""
        grouped = defaultdict(list)
        for article in articles:
            date = article['publish_time'][:10]  # 提取日期部分
            grouped[date].append(article)
        return dict(sorted(grouped.items(), reverse=True))

    def _generate_markdown(self, date: str, grouped: Dict[str, List[Dict]], all_articles: List[Dict]) -> str:
        """
        生成每日摘要Markdown内容

        Args:
            date: 日期
            grouped: 按公众号分组的文章
            all_articles: 所有文章列表

        Returns:
            Markdown内容
        """
        lines = []

        # 标题
        lines.append(f"# 微信公众号每日摘要 - {date}\n")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # 统计信息
        lines.append("## 📊 今日统计\n")
        lines.append(f"- **文章总数**: {len(all_articles)} 篇")
        lines.append(f"- **公众号数**: {len(grouped)} 个")
        lines.append("")

        # 目录
        lines.append("## 📑 目录\n")
        for i, account in enumerate(sorted(grouped.keys()), 1):
            lines.append(f"{i}. [{account}](#{self._anchor(account)}) ({len(grouped[account])} 篇)")
        lines.append("")

        # 按公众号列出文章
        lines.append("---\n")
        lines.append("## 📰 文章列表\n")

        for account in sorted(grouped.keys()):
            articles = grouped[account]

            # 公众号标题
            lines.append(f"### {account}\n")
            lines.append(f"*共 {len(articles)} 篇文章*\n")

            # 文章列表
            for i, article in enumerate(articles, 1):
                lines.append(f"#### {i}. {article['title']}\n")

                if article['author'] and article['author'] != account:
                    lines.append(f"**作者**: {article['author']}  ")

                lines.append(f"**发布时间**: {article['publish_time']}  ")

                if article['summary']:
                    lines.append(f"\n**摘要**: {article['summary']}\n")

                if article['url']:
                    lines.append(f"**阅读链接**: [{article['url']}]({article['url']})\n")

                lines.append("")

            lines.append("---\n")

        # 页脚
        lines.append("\n---\n")
        lines.append("*本摘要由微信公众号爬虫自动生成*")

        return "\n".join(lines)

    def _generate_weekly_markdown(self, start_date: str, end_date: str, grouped_by_date: Dict) -> str:
        """
        生成周摘要Markdown内容

        Args:
            start_date: 开始日期
            end_date: 结束日期
            grouped_by_date: 按日期分组的文章

        Returns:
            Markdown内容
        """
        lines = []

        # 标题
        lines.append(f"# 微信公众号周摘要\n")
        lines.append(f"**时间范围**: {start_date} 至 {end_date}\n")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # 统计信息
        total_articles = sum(len(articles) for articles in grouped_by_date.values())
        all_accounts = set()
        for articles in grouped_by_date.values():
            for article in articles:
                all_accounts.add(article['account_name'])

        lines.append("## 📊 本周统计\n")
        lines.append(f"- **文章总数**: {total_articles} 篇")
        lines.append(f"- **公众号数**: {len(all_accounts)} 个")
        lines.append(f"- **活跃天数**: {len(grouped_by_date)} 天")
        lines.append("")

        # 按日期列出文章
        lines.append("---\n")
        lines.append("## 📅 按日期浏览\n")

        for date in sorted(grouped_by_date.keys(), reverse=True):
            articles = grouped_by_date[date]
            weekday = datetime.strptime(date, '%Y-%m-%d').strftime('%A')

            lines.append(f"### {date} ({weekday})\n")
            lines.append(f"*{len(articles)} 篇文章*\n")

            # 按公众号分组
            account_grouped = self._group_by_account(articles)

            for account in sorted(account_grouped.keys()):
                account_articles = account_grouped[account]
                lines.append(f"#### 📱 {account}\n")

                for article in account_articles:
                    lines.append(f"- **{article['title']}**")
                    if article['url']:
                        lines.append(f"  - [阅读原文]({article['url']})")
                    lines.append("")

            lines.append("")

        # 页脚
        lines.append("\n---\n")
        lines.append("*本周摘要由微信公众号爬虫自动生成*")

        return "\n".join(lines)

    def _anchor(self, text: str) -> str:
        """生成Markdown锚点"""
        # 简化版本，仅用于演示
        return text.replace(' ', '-').lower()


if __name__ == "__main__":
    # 测试代码
    generator = DigestGenerator()

    # 生成今日摘要
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"生成 {today} 的每日摘要...")
    generator.generate_daily_digest(today)

    # 生成周摘要
    print("\n生成最近7天的周摘要...")
    generator.generate_weekly_digest()

    print("\n✓ 摘要生成完成")
