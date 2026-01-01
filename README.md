# 微信公众号自动爬虫与每日摘要系统

一个自动化爬取微信公众号文章并生成每日摘要的 Python 工具。

## 功能特性

- 自动爬取指定微信公众号的最新文章
- 基于 SQLite 的本地文章数据库存储
- 每日自动生成 Markdown 格式的文章摘要
- 支持周摘要生成
- 定时任务自动执行
- 灵活的配置管理

## 项目结构

```
.
├── article_storage.py      # 文章数据库管理模块
├── wechat_scraper.py       # 微信公众号爬虫模块
├── digest_generator.py     # 摘要生成器模块
├── scheduler.py            # 定时任务调度器
├── config.yaml.example     # 配置文件示例
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略文件
├── wechat_articles.db     # SQLite 数据库（自动生成）
└── digests/               # 摘要输出目录（自动生成）
```

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd hello-jiajia
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

复制配置文件示例并根据需要修改：

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml`，添加你想关注的公众号：

```yaml
accounts:
  - "人民日报"
  - "新华社"
  - "你关注的公众号"

scrape_time: "08:00"    # 每日爬取时间
digest_time: "20:00"    # 每日摘要生成时间
max_pages: 3            # 每次爬取的页数
```

## 使用方法

### 方式一：立即执行任务（测试用）

```bash
# 立即爬取文章
python scheduler.py --run-now scrape

# 立即生成每日摘要
python scheduler.py --run-now digest

# 立即生成周摘要
python scheduler.py --run-now weekly

# 执行所有任务
python scheduler.py --run-now all
```

### 方式二：启动定时调度器

```bash
# 使用默认配置文件 config.yaml
python scheduler.py

# 使用自定义配置文件
python scheduler.py --config my_config.yaml
```

调度器将按照配置文件中的时间自动执行爬取和摘要生成任务。

### 方式三：单独使用各模块

#### 测试爬虫

```bash
python wechat_scraper.py
```

#### 测试摘要生成

```bash
python digest_generator.py
```

#### 测试数据库

```bash
python article_storage.py
```

## 模块说明

### 1. article_storage.py - 数据存储模块

管理 SQLite 数据库，提供文章的增删改查功能。

**主要功能：**
- 添加文章到数据库
- 按日期查询文章
- 按公众号查询文章
- 获取统计信息

### 2. wechat_scraper.py - 爬虫模块

通过搜狗微信搜索抓取公众号文章。

**主要功能：**
- 搜索公众号
- 爬取文章列表
- 解析文章信息（标题、作者、发布时间、摘要等）
- 批量爬取多个公众号

**注意事项：**
- 使用搜狗微信搜索接口，无需登录
- 设置了随机延迟，避免被封禁
- 频繁爬取可能触发反爬机制，建议适度使用

### 3. digest_generator.py - 摘要生成模块

将数据库中的文章整理成 Markdown 格式的文档。

**主要功能：**
- 生成每日摘要（按公众号分组）
- 生成周摘要（按日期分组）
- 自动统计文章数量

**输出格式：**
- 每日摘要：`digests/digest_YYYY-MM-DD.md`
- 周摘要：`digests/weekly_digest_YYYY-MM-DD_to_YYYY-MM-DD.md`

### 4. scheduler.py - 任务调度模块

基于 `schedule` 库实现定时任务。

**主要功能：**
- 每日定时爬取
- 每日定时生成摘要
- 每周定时生成周摘要
- 日志记录

## 进阶使用

### 使用 systemd 实现开机自启（Linux）

创建服务文件 `/etc/systemd/system/wechat-scraper.service`：

```ini
[Unit]
Description=WeChat Article Scraper
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/hello-jiajia
ExecStart=/usr/bin/python3 /path/to/hello-jiajia/scheduler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable wechat-scraper
sudo systemctl start wechat-scraper
```

### 使用 cron 定时执行（Linux/Mac）

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天 8:00 爬取，20:00 生成摘要）
0 8 * * * cd /path/to/hello-jiajia && /usr/bin/python3 scheduler.py --run-now scrape
0 20 * * * cd /path/to/hello-jiajia && /usr/bin/python3 scheduler.py --run-now digest
```

### 使用 Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天特定时间）
4. 操作：启动程序
   - 程序：`python.exe`
   - 参数：`scheduler.py --run-now scrape`
   - 起始于：项目目录路径

## 数据库结构

### articles 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 文章标题 |
| account_name | TEXT | 公众号名称 |
| author | TEXT | 作者 |
| url | TEXT | 文章链接（唯一） |
| publish_time | TEXT | 发布时间 |
| content | TEXT | 文章内容 |
| summary | TEXT | 摘要 |
| cover_image | TEXT | 封面图片 |
| read_count | INTEGER | 阅读数 |
| like_count | INTEGER | 点赞数 |
| scraped_time | TEXT | 爬取时间 |
| tags | TEXT | 标签（JSON） |
| is_read | BOOLEAN | 是否已读 |

### accounts 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 公众号名称（唯一） |
| description | TEXT | 描述 |
| last_update | TEXT | 最后更新时间 |
| article_count | INTEGER | 文章数量 |

## 常见问题

### Q: 爬虫无法获取文章？

A: 可能的原因：
1. 公众号名称不准确，请使用完整的公众号名称
2. 搜狗微信搜索触发了反爬机制，建议减少爬取频率或更换 IP
3. 网络连接问题

### Q: 如何查看爬取到的文章？

A: 有两种方式：
1. 查看生成的摘要文件：`digests/digest_YYYY-MM-DD.md`
2. 直接查询数据库：使用 SQLite 工具打开 `wechat_articles.db`

### Q: 摘要文件在哪里？

A: 默认保存在 `digests/` 目录下，可以在配置文件中修改输出目录。

### Q: 如何添加更多公众号？

A: 编辑 `config.yaml`，在 `accounts` 列表中添加公众号名称。

## 免责声明

本项目仅用于学习和个人使用，请遵守相关法律法规和微信公众平台的使用条款。
- 请勿用于商业用途
- 请勿过度频繁爬取，避免对服务器造成压力
- 尊重内容版权，爬取的内容仅供个人阅读

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2026-01-01)
- 初始版本
- 实现基本爬虫功能
- 实现每日和周摘要生成
- 实现定时任务调度
