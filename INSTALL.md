# 安装和运行指南 - Mac 系统

## 更新说明

系统已升级为使用 **Playwright 直接爬取微信公众号**，解决了搜狗微信搜索的以下问题：
- ❌ 搜狗有 3-7 天延迟（最新文章无法及时获取）
- ❌ 搜狗内容不全（部分文章未被收录）

新方法：
- ✅ 实时爬取（无延迟）
- ✅ 完整覆盖（获取所有历史文章）
- ✅ 时间范围精确（爬取上周所有文章）

---

## 第一步：拉取最新代码

打开终端（Terminal.app），运行：

```bash
cd ~/hello-jiajia
git pull origin claude/wechat-scraper-digest-DfnHz
```

---

## 第二步：安装 Playwright

### 2.1 安装 Playwright 库

```bash
pip3 install playwright
```

如果遇到网络问题，可以使用国内镜像：

```bash
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright
```

### 2.2 安装 Chromium 浏览器

```bash
playwright install chromium
```

或者使用 Python 模块方式：

```bash
python3 -m playwright install chromium
```

**注意**：这一步会下载 Chromium 浏览器（约 150-200MB），需要一些时间。

如果下载失败，可以设置环境变量使用国内镜像：

```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python3 -m playwright install chromium
```

---

## 第三步：测试爬虫

运行测试脚本，验证 Playwright 爬虫是否正常工作：

```bash
cd ~/hello-jiajia
python3 wechat_scraper_direct.py
```

### 预期输出

如果一切正常，你应该看到类似输出：

```
============================================================
开始爬取公众号: 光储星球
爬取方式: 直接访问微信历史消息页面
时间范围: 2025-12-25 至 2026-01-01
============================================================

正在访问历史消息页面...
正在加载文章列表...
正在滚动加载... (1/30)
  找到 15 个文章元素 (使用选择器: .weui_media_box)
  ✓ [12-31 10:30] 文章标题示例...
  ✓ [12-30 08:00] 另一篇文章...
...

爬取完成: 共获取 XX 篇文章

保存文章到数据库...
  ✓ 保存: 文章标题...
  ✗ 已存在: 文章标题...

============================================================
爬取完成: 获取 XX 篇文章，保存 XX 篇新文章
============================================================
```

### 如果遇到问题

1. **未找到文章元素**：微信页面结构可能变化，请截图发给我分析
2. **连接超时**：检查网络连接，或者增加超时时间
3. **403 错误**：可能需要验证码或登录，这种情况需要调整策略

---

## 第四步：运行完整周爬取

测试成功后，运行完整的周爬取 + 摘要生成：

```bash
python3 scheduler.py --run-now weekly
```

这将：
1. 爬取"光储星球"公众号上周（最近7天）的所有文章
2. 保存到数据库
3. 自动生成 Markdown 格式的周摘要

摘要文件保存在 `digests/` 目录，例如：
```
digests/weekly_digest_2025-12-25_to_2026-01-01.md
```

---

## 第五步：设置自动运行（可选）

### 方法1：使用内置调度器（推荐）

直接运行 scheduler.py，它会在后台等待，每周一早上9点自动执行：

```bash
# 前台运行（可以看到日志）
python3 scheduler.py

# 后台运行
nohup python3 scheduler.py > scraper.log 2>&1 &
```

### 方法2：使用 launchd（Mac 原生方式）

创建 plist 文件：

```bash
nano ~/Library/LaunchAgents/com.wechat.scraper.plist
```

内容：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wechat.scraper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/你的用户名/hello-jiajia/scheduler.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>  <!-- 1 = 周一 -->
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/你的用户名/hello-jiajia/scraper.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/你的用户名/hello-jiajia/scraper_error.log</string>
</dict>
</plist>
```

**注意**：替换 `/Users/你的用户名/` 为你的实际路径。

加载任务：

```bash
launchctl load ~/Library/LaunchAgents/com.wechat.scraper.plist
```

---

## 配置说明

当前配置（`config.yaml`）：

```yaml
# 爬取方式：direct = 直接爬取（实时）
scrape_method: "direct"

# 监控的公众号
accounts:
  - "光储星球"

# 每周一早上9点爬取
scrape_schedule:
  enabled: true
  day: "monday"
  time: "09:00"

# 爬取时间范围：最近7天
days: 7
```

如果需要修改：
- **更改爬取时间**：修改 `day` 和 `time`
- **更改时间范围**：修改 `days`（例如改为 14 天）
- **切换回搜狗方式**：改为 `scrape_method: "sogou"`（不推荐）

---

## 常用命令

```bash
# 立即爬取 + 生成摘要
python3 scheduler.py --run-now weekly

# 仅爬取文章
python3 scheduler.py --run-now scrape

# 仅生成摘要（使用数据库已有数据）
python3 scheduler.py --run-now digest

# 查看数据库统计
python3 article_storage.py

# 查看日志
tail -f scraper.log
```

---

## 故障排查

### Playwright 安装失败

```bash
# 方法1：使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python3 -m playwright install chromium

# 方法2：手动指定浏览器路径
# 如果已有 Chrome，可以配置使用系统 Chrome
```

### 爬取失败或无内容

1. 检查网络连接
2. 查看错误截图：`error_screenshot.png`
3. 尝试增加等待时间（修改 wechat_scraper_direct.py 中的 `asyncio.sleep` 参数）
4. 微信页面结构可能变化，需要更新选择器

### 需要验证码

如果微信要求验证码：
- 方案1：在 Playwright 中设置 `headless=False`，手动完成验证
- 方案2：使用已登录的 Cookie（需要额外配置）

---

## 技术支持

如有任何问题，请提供以下信息：
1. 错误日志（`scraper.log`）
2. 错误截图（`error_screenshot.png`）
3. 运行命令和输出

## 总结

核心优势：
- ✅ **实时性**：无延迟，获取最新文章
- ✅ **完整性**：不漏掉任何文章
- ✅ **准确性**：精确的时间范围过滤
- ✅ **自动化**：每周自动运行，无需人工干预
