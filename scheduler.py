#!/usr/bin/env python3
"""
定时任务调度器
自动化执行爬取和摘要生成任务
"""

import schedule
import time
import yaml
import os
from datetime import datetime
from wechat_scraper import WeChatScraper
from digest_generator import DigestGenerator
from article_storage import ArticleStorage
import logging


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """定时任务调度器"""

    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化调度器

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.storage = ArticleStorage()
        self.scraper = WeChatScraper(self.storage)
        self.generator = DigestGenerator(self.storage)

    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        if not os.path.exists(config_file):
            logger.warning(f"配置文件 {config_file} 不存在，使用默认配置")
            return self._get_default_config()

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"成功加载配置文件: {config_file}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            'accounts': ['光储星球'],
            'scrape_schedule': {
                'enabled': True,
                'day': 'monday',
                'time': '09:00'
            },
            'weekly_digest': {
                'enabled': True,
                'generate_after_scrape': True
            },
            'days': 7,  # 爬取最近7天的文章
            'scrape_time': '08:00',
            'digest_time': '20:00',
            'enable_weekly_digest': False,
            'weekly_digest_day': 'sunday',
            'weekly_digest_time': '21:00'
        }

    def scrape_task(self):
        """爬取任务（按时间范围）"""
        try:
            logger.info("=" * 60)
            logger.info("开始执行爬取任务")
            logger.info("=" * 60)

            accounts = self.config.get('accounts', [])
            days = self.config.get('days', 7)  # 默认爬取最近7天

            if not accounts:
                logger.warning("配置中没有公众号列表，跳过爬取任务")
                return

            logger.info(f"目标: 爬取最近 {days} 天的文章")
            self.scraper.scrape_multiple_accounts(accounts, days)

            # 显示统计
            stats = self.storage.get_statistics()
            logger.info("数据库统计:")
            logger.info(f"  总文章数: {stats['total_articles']}")
            logger.info(f"  公众号数: {stats['total_accounts']}")
            logger.info(f"  今日新增: {stats['today_count']}")

            logger.info("爬取任务完成")

        except Exception as e:
            logger.error(f"爬取任务执行失败: {e}", exc_info=True)

    def digest_task(self):
        """每日摘要生成任务"""
        try:
            logger.info("=" * 60)
            logger.info("开始生成每日摘要")
            logger.info("=" * 60)

            today = datetime.now().strftime('%Y-%m-%d')
            filepath = self.generator.generate_daily_digest(today)

            if filepath:
                logger.info(f"每日摘要已生成: {filepath}")
            else:
                logger.warning("今日没有文章，未生成摘要")

        except Exception as e:
            logger.error(f"摘要生成任务执行失败: {e}", exc_info=True)

    def weekly_digest_task(self):
        """周摘要生成任务"""
        try:
            logger.info("=" * 60)
            logger.info("开始生成周摘要")
            logger.info("=" * 60)

            filepath = self.generator.generate_weekly_digest()

            if filepath:
                logger.info(f"周摘要已生成: {filepath}")
            else:
                logger.warning("本周没有文章，未生成摘要")

        except Exception as e:
            logger.error(f"周摘要生成任务执行失败: {e}", exc_info=True)

    def weekly_scrape_and_digest_task(self):
        """每周爬取并生成摘要的组合任务"""
        try:
            logger.info("=" * 60)
            logger.info("开始执行每周任务：爬取文章 + 生成周摘要")
            logger.info("=" * 60)

            # 先执行爬取
            self.scrape_task()

            # 等待一小会儿，确保数据写入完成
            import time
            time.sleep(2)

            # 生成周摘要
            self.weekly_digest_task()

            logger.info("=" * 60)
            logger.info("每周任务完成")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"每周任务执行失败: {e}", exc_info=True)

    def setup_schedule(self):
        """设置定时任务"""
        # 检查新配置格式（每周爬取）
        scrape_schedule = self.config.get('scrape_schedule', {})
        if scrape_schedule.get('enabled', False):
            # 每周爬取模式
            day = scrape_schedule.get('day', 'monday').lower()
            time_str = scrape_schedule.get('time', '09:00')

            day_map = {
                'monday': schedule.every().monday,
                'tuesday': schedule.every().tuesday,
                'wednesday': schedule.every().wednesday,
                'thursday': schedule.every().thursday,
                'friday': schedule.every().friday,
                'saturday': schedule.every().saturday,
                'sunday': schedule.every().sunday
            }

            if day in day_map:
                # 检查是否需要在爬取后自动生成摘要
                weekly_digest_config = self.config.get('weekly_digest', {})
                if weekly_digest_config.get('generate_after_scrape', False):
                    # 组合任务：爬取 + 生成摘要
                    day_map[day].at(time_str).do(self.weekly_scrape_and_digest_task)
                    logger.info(f"✓ 已设置每周任务（爬取+摘要）: 每周{day} {time_str}")
                else:
                    # 仅爬取
                    day_map[day].at(time_str).do(self.scrape_task)
                    logger.info(f"✓ 已设置每周爬取任务: 每周{day} {time_str}")

        # 兼容旧的每日配置格式
        if self.config.get('daily_scrape_enabled', False):
            scrape_time = self.config.get('scrape_time', '08:00')
            schedule.every().day.at(scrape_time).do(self.scrape_task)
            logger.info(f"✓ 已设置每日爬取任务: {scrape_time}")

        if self.config.get('daily_digest_enabled', False):
            digest_time = self.config.get('digest_time', '20:00')
            schedule.every().day.at(digest_time).do(self.digest_task)
            logger.info(f"✓ 已设置每日摘要任务: {digest_time}")

        # 旧的周摘要配置（独立执行）
        if self.config.get('enable_weekly_digest', False) and not scrape_schedule.get('enabled', False):
            weekly_day = self.config.get('weekly_digest_day', 'sunday').lower()
            weekly_time = self.config.get('weekly_digest_time', '21:00')

            day_map = {
                'monday': schedule.every().monday,
                'tuesday': schedule.every().tuesday,
                'wednesday': schedule.every().wednesday,
                'thursday': schedule.every().thursday,
                'friday': schedule.every().friday,
                'saturday': schedule.every().saturday,
                'sunday': schedule.every().sunday
            }

            if weekly_day in day_map:
                day_map[weekly_day].at(weekly_time).do(self.weekly_digest_task)
                logger.info(f"✓ 已设置周摘要任务: 每周{weekly_day} {weekly_time}")

    def run_now(self, task: str = "all"):
        """
        立即执行任务（用于测试）

        Args:
            task: 任务类型 ("scrape", "digest", "weekly", "all")
        """
        if task in ["scrape", "all"]:
            self.scrape_task()

        if task in ["digest", "all"]:
            self.digest_task()

        if task in ["weekly", "all"]:
            self.weekly_digest_task()

    def start(self):
        """启动调度器"""
        logger.info("\n" + "=" * 60)
        logger.info("微信公众号爬虫调度器启动")
        logger.info("=" * 60)

        # 显示配置
        logger.info("\n当前配置:")
        logger.info(f"  监控公众号: {', '.join(self.config.get('accounts', []))}")
        logger.info(f"  时间范围: 最近 {self.config.get('days', 7)} 天")

        # 显示爬取调度
        scrape_schedule = self.config.get('scrape_schedule', {})
        if scrape_schedule.get('enabled', False):
            day_cn = {
                'monday': '周一', 'tuesday': '周二', 'wednesday': '周三',
                'thursday': '周四', 'friday': '周五', 'saturday': '周六', 'sunday': '周日'
            }
            day = scrape_schedule.get('day', 'monday').lower()
            time_str = scrape_schedule.get('time', '09:00')
            logger.info(f"  爬取计划: 每{day_cn.get(day, day)} {time_str}")

            weekly_digest_config = self.config.get('weekly_digest', {})
            if weekly_digest_config.get('generate_after_scrape', False):
                logger.info(f"  周摘要: 爬取完成后自动生成")
        else:
            # 旧配置格式
            if self.config.get('daily_scrape_enabled', False):
                logger.info(f"  爬取时间: 每天 {self.config.get('scrape_time', '08:00')}")
            if self.config.get('daily_digest_enabled', False):
                logger.info(f"  摘要时间: 每天 {self.config.get('digest_time', '20:00')}")
            if self.config.get('enable_weekly_digest', False):
                logger.info(f"  周摘要: 启用 (每周{self.config.get('weekly_digest_day', 'sunday')} {self.config.get('weekly_digest_time', '21:00')})")

        # 设置定时任务
        self.setup_schedule()

        logger.info("\n调度器运行中... (按 Ctrl+C 停止)\n")

        # 运行调度器
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("\n调度器已停止")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='微信公众号爬虫调度器')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--run-now', choices=['scrape', 'digest', 'weekly', 'all'],
                        help='立即执行任务（用于测试）')

    args = parser.parse_args()

    scheduler = TaskScheduler(args.config)

    if args.run_now:
        # 立即执行任务
        scheduler.run_now(args.run_now)
    else:
        # 启动调度器
        scheduler.start()


if __name__ == "__main__":
    main()
