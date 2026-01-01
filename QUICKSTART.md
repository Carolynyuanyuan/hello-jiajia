# 快速开始 - 5分钟上手指南

## 🎯 目标
在你的 Mac 上设置微信公众号"光储星球"的自动爬虫，每周一早上9点自动爬取上周文章并生成摘要。

---

## 📋 三步走

### 步骤 1: 拉取最新代码

打开终端（Terminal），运行：

```bash
cd ~/hello-jiajia
git pull origin claude/wechat-scraper-digest-DfnHz
```

---

### 步骤 2: 安装 Playwright

```bash
# 安装 Playwright
pip3 install playwright

# 安装 Chromium 浏览器（约150MB，需要几分钟）
playwright install chromium
```

**如果下载慢**，使用国内镜像：

```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python3 -m playwright install chromium
```

---

### 步骤 3: 测试运行

```bash
# 立即测试爬取 + 生成摘要
python3 scheduler.py --run-now weekly
```

查看生成的摘要文件：

```bash
ls -l digests/
cat digests/weekly_digest_*.md
```

---

## ✅ 完成！

如果测试成功，你可以：

### 选项 A: 后台运行（推荐）

```bash
# 启动后台调度器，每周一早上9点自动运行
nohup python3 scheduler.py > scraper.log 2>&1 &

# 查看日志
tail -f scraper.log
```

### 选项 B: 使用 Mac 系统服务

参考 `INSTALL.md` 中的 launchd 配置。

---

## 🔧 核心配置

配置文件：`config.yaml`

```yaml
scrape_method: "direct"  # 直接爬取（实时、完整）
accounts:
  - "光储星球"
scrape_schedule:
  day: "monday"          # 每周一
  time: "09:00"          # 早上9点
days: 7                  # 爬取最近7天
```

---

## 📊 查看结果

每周摘要保存在 `digests/` 目录：

```
digests/
└── weekly_digest_2025-12-25_to_2026-01-01.md
```

打开摘要文件查看：
- 📰 文章标题
- 📅 发布时间
- 📝 内容摘要
- 🔗 阅读链接

---

## 🆘 遇到问题？

1. **Playwright 安装失败** → 查看 `INSTALL.md` 故障排查章节
2. **爬取无内容** → 检查 `error_screenshot.png`
3. **其他问题** → 查看 `scraper.log` 日志文件

详细文档：
- `INSTALL.md` - 完整安装和配置指南
- `USAGE.md` - 详细使用说明

---

## 🎉 新版本优势

相比之前的搜狗方式：

| 特性 | 搜狗方式 | 新版（直接爬取） |
|------|---------|----------------|
| 延迟 | ❌ 3-7天 | ✅ 实时 |
| 完整性 | ❌ 部分缺失 | ✅ 完整覆盖 |
| 准确性 | ⚠️ 不稳定 | ✅ 精确时间范围 |
| 依赖 | 搜狗API | Playwright |

---

**就是这么简单！** 🚀
