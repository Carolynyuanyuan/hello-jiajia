# 光储星球 - 微信公众号爬虫使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 使用快捷脚本（推荐）

#### Linux/Mac:
```bash
./run.sh
```

#### Windows:
双击运行 `run.bat` 或在命令行执行：
```cmd
run.bat
```

## 功能说明

### 自动化模式

系统已配置为**每周一早上9:00**自动执行以下任务：
1. 爬取"光储星球"公众号上周的文章（最多50篇，5页）
2. 自动生成周摘要文档（Markdown格式）

### 手动测试

如果想立即测试，可以运行：

```bash
# 立即爬取并生成摘要
python scheduler.py --run-now weekly
```

## 生成的文件

### 摘要文档位置
所有摘要文档保存在 `digests/` 目录下：

```
digests/
└── weekly_digest_2026-01-01_to_2026-01-08.md
```

### 摘要文档格式

每篇文章包含：
- **文章标题**
- **发布时间**
- **内容摘要**（搜狗微信搜索提供的摘要）
- **阅读链接**

示例：
```markdown
# 光储星球 - 本周文章摘要

**时间范围**: 2026-01-01 至 2026-01-08

## 📊 本周统计
- **文章总数**: 15 篇

## 📰 文章列表

### 📅 2026-01-07 (星期二)

#### 1. 光伏行业2026年展望

**发布时间**: 2026-01-07 10:30:00

**内容摘要**:
本文分析了2026年光伏行业的发展趋势，包括技术创新、市场规模和政策支持等方面...

**阅读链接**: [https://mp.weixin.qq.com/s/...]

---
```

## 配置说明

当前配置文件 `config.yaml`：

```yaml
# 监控的公众号
accounts:
  - "光储星球"

# 每周一早上9点爬取
scrape_schedule:
  enabled: true
  day: "monday"
  time: "09:00"

# 自动生成周摘要
weekly_digest:
  enabled: true
  generate_after_scrape: true

# 每次爬取5页（约50篇文章，覆盖一周内容）
max_pages: 5
```

## 常用操作

### 1. 启动定时调度器

```bash
python scheduler.py
```

系统将在后台运行，每周一早上9点自动执行任务。

**提示**：可以使用 `nohup` 或 `screen` 让程序在后台持续运行：

```bash
# Linux/Mac 后台运行
nohup python scheduler.py > scraper.log 2>&1 &

# 或使用 screen
screen -S wechat-scraper
python scheduler.py
# 按 Ctrl+A 然后按 D 退出 screen
```

### 2. 立即测试爬取

```bash
# 爬取文章 + 生成周摘要
python scheduler.py --run-now weekly

# 仅爬取文章
python scheduler.py --run-now scrape

# 仅生成周摘要（使用数据库中已有数据）
python scheduler.py --run-now digest
```

### 3. 查看数据库统计

```bash
python article_storage.py
```

### 4. 查看日志

```bash
tail -f scheduler.log
```

## 修改配置

如果需要调整配置，编辑 `config.yaml`：

### 更改爬取时间

```yaml
scrape_schedule:
  enabled: true
  day: "friday"      # 改为周五
  time: "18:00"      # 改为晚上6点
```

### 添加更多公众号

```yaml
accounts:
  - "光储星球"
  - "另一个公众号"
  - "第三个公众号"
```

### 调整爬取页数

```yaml
max_pages: 3  # 减少到3页（约30篇文章）
```

## 摘要内容说明

**关于文章摘要**：
- 摘要来自搜狗微信搜索的自动提取
- 通常为文章前几段的精简内容
- 部分文章可能没有摘要（显示"暂无摘要"）

**阅读完整内容**：
- 点击每篇文章的"阅读链接"可查看完整文章
- 链接会跳转到微信公众号文章页面

## 常见问题

### Q: 为什么有些文章没有摘要？

A: 搜狗微信搜索对某些文章可能无法自动提取摘要，这是正常现象。文章标题和链接仍然可用。

### Q: 可以爬取文章的完整内容吗？

A: 由于微信公众号的限制，爬取完整内容需要模拟登录或使用更复杂的技术，当前版本只提供搜狗搜索的摘要。建议通过提供的链接阅读完整文章。

### Q: 爬虫会被封禁吗？

A: 系统已设置随机延迟和合理的爬取频率。每周只爬取一次，每次5页，风险较低。但仍建议：
- 不要频繁手动测试
- 不要大幅增加 `max_pages` 值
- 如遇访问限制，等待几小时后再试

### Q: 如何在服务器上持续运行？

A: 推荐使用以下方法之一：

**方法1: systemd (Linux)**
创建服务文件（见 README.md）

**方法2: cron + screen**
```bash
# 使用 screen 启动
screen -S wechat-scraper
python scheduler.py
# Ctrl+A, D 退出

# 重新连接
screen -r wechat-scraper
```

**方法3: nohup**
```bash
nohup python scheduler.py > scraper.log 2>&1 &
```

### Q: 如何查看上周生成的摘要？

A: 所有摘要文件都保存在 `digests/` 目录，文件名包含日期范围，按日期查找即可。

## 技术支持

如有问题，请查看：
1. `scheduler.log` - 运行日志
2. `README.md` - 完整技术文档
3. 数据库文件 `wechat_articles.db` - 可使用 SQLite 工具查看

## 免责声明

本工具仅用于个人学习和阅读，请勿用于商业用途。请遵守相关法律法规和微信公众平台使用条款。
