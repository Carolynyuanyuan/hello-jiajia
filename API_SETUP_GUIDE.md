# 微信 API 爬虫使用指南

## 🎉 完全自动化方案！

通过微信公众号后台 API 实现**实时、完整、稳定**的文章爬取，无需手动复制链接！

---

## ✅ 优势对比

| 方案 | 实时性 | 完整性 | 稳定性 | 自动化 |
|------|--------|--------|--------|--------|
| **API 方式** | ✅ 实时 | ✅ 100% | ✅ 高 | ✅ 全自动 |
| 搜狗方式 | ❌ 3-7天延迟 | ⚠️ 80-90% | ✅ 高 | ✅ 全自动 |
| 直接爬取 | ✅ 实时 | ✅ 100% | ❌ 被拦截 | ❌ 无法使用 |

---

## 📋 配置步骤（仅需5分钟）

### 步骤 1：拉取最新代码

```bash
cd ~/hello-jiajia
git pull origin claude/wechat-scraper-digest-DfnHz
```

---

### 步骤 2：创建 API 配置文件

```bash
# 复制模板
cp wechat_api_config.txt.example wechat_api_config.txt

# 编辑配置文件
nano wechat_api_config.txt
```

或者直接用命令创建：

```bash
cat > wechat_api_config.txt << 'EOF'
# Token: 从浏览器地址栏 URL 中提取（例如：token=759683668）
token=759683668

# Cookie: 从浏览器开发者工具复制的完整 Cookie 字符串
cookie=rewardsn=; wxtokenkey=777; mm_lang=zh_CN; ua_id=7JCyVPQy4MgPBj7BAAAAAJHIQG0m-GMHxGQALmmWK5I=; _clck=13o00m9|1|g2c|0; wxuin=67270559065661; mm_lang=zh_CN; uuid=31172c10b0bb34bba5d170bbc15c2253; rand_info=CAESIE+94ksF63pbyuZWVmt4NcWcgLEayzca1Dk/qC5LIJQW; slave_bizuin=3882927934; data_bizuin=3882927934; bizuin=3882927934; data_ticket=1gRtG6RfY/LizxQGsJXywe0jdv42/ZtsUQHy7vv0CCYka8B6IpnG1y35z+gwZ3bY; slave_sid=RWxKVFg3eXR0NzNpVDVMalRiNXJ5Y3ZrRl9YdmVBT2hreXhfdlpweFB2ZHVaVkFwdFBGeThKM2hRZGpScDkyVVJ6YmxvZUx2SkZLTUxSM3Q1WHRmYTR6NUE3Q2dHN0x0VzRIcU84SGwyOVg1Tlp4eVV2aFJnbTNiSXhvUEZLbjBVOXRhVmpaVG03Mm03NW9j; slave_user=gh_fd7567309352; xid=063ca195f920ef515e53ee69f0b3bf4e; mmad_session=3eaf97143d075ff3869f9bc15eeae8ae581700a7b341749c302674fcf0a9cb98e8a1796083cbcef3fdb2b9066827c2f2129d5ce3dc601b9a1d1cd520cd43f5c665b3f08ef499e4997246bce86641270a86cb60af5c08f9a62a01e4cd5fd5727d11de1c56c245721266e7088080fefde3; pgv_info=ssid=s3069300738; ts_last=mp.weixin.qq.com/cgi-bin/frame; pgv_pvid=5905148580; ts_uid=5937438824; _clsk=qlqpjz|1767273100878|25|1|mp.weixin.qq.com/weheat-agent/payload/record
EOF
```

**注意**：把上面的 `token` 和 `cookie` 替换成你自己的！

---

### 步骤 3：如何获取 Token 和 Cookie？

#### 获取 Token：

1. 在微信公众号后台登录
2. 查看浏览器地址栏 URL
3. 找到 `token=XXXXXX` 部分
4. 复制数字部分（例如：`759683668`）

#### 获取 Cookie：

1. 打开浏览器开发者工具（`Command + Option + I`）
2. 切换到 **Network（网络）** 标签
3. 在公众号后台随便点击一个功能
4. 在 Network 中找到任意一个请求
5. 点击请求，查看 **Request Headers（请求标头）**
6. 找到 **Cookie:** 那一行
7. 复制整个 Cookie 字符串（从 `rewardsn=` 开始到最后）

**你已经有了！** 就是你之前给我的那串 Cookie！

---

### 步骤 4：更新配置文件

编辑 `config.yaml`，确保使用 `api` 方式：

```bash
nano config.yaml
```

确认这一行：
```yaml
scrape_method: "api"
```

（应该已经是 `"api"` 了，如果不是就改成 `"api"`）

---

### 步骤 5：测试运行

```bash
# 测试 API 爬虫
python3 wechat_api_scraper.py
```

### 预期输出：

```
============================================================
开始爬取公众号: 光储星球
爬取方式: 微信后台 API
时间范围: 2025-12-25 至 2026-01-01
============================================================

正在获取第 1 - 20 篇文章...
  ✓ [12-31 11:50] 华尔街大鳄入局，章鱼能源旗下Kraken完成10亿美元融资！...
  ✓ [12-31 11:50] SolarEdge工商业储能系统正式登陆德国市场！...
  ✓ [12-30 18:30] 全球首款800V浸没式冷却电池储能发布，进军AIDC领域...
  ...

爬取完成: 共获取 XX 篇文章

保存文章到数据库...
  ✓ 保存: 华尔街大鳄入局，章鱼能源旗下Kraken完成10亿...
  ✓ 保存: SolarEdge工商业储能系统正式登陆德国市场！...
  ...

============================================================
爬取完成: 获取 XX 篇文章，保存 XX 篇新文章
============================================================
```

---

### 步骤 6：运行完整流程（爬取 + 生成摘要）

```bash
python3 scheduler.py --run-now weekly
```

查看生成的摘要：

```bash
ls -l digests/
cat digests/weekly_digest_*.md
```

---

## 🔧 工作原理

### API 调用流程：

1. **调用微信后台 API**
   ```
   GET /cgi-bin/appmsgpublish?fakeid=XXX&token=XXX&...
   ```

2. **获取 JSON 响应**
   包含文章标题、链接、摘要、发布时间等完整信息

3. **时间过滤**
   只保存最近 7 天的文章

4. **保存到数据库**
   自动去重，避免重复保存

5. **生成 Markdown 摘要**
   包含标题、时间、摘要、链接

---

## 🚀 自动化运行

### 选项 A：后台运行调度器

```bash
# 启动后台调度器（每周一早上9点自动运行）
nohup python3 scheduler.py > scraper.log 2>&1 &

# 查看日志
tail -f scraper.log
```

### 选项 B：使用 Mac 系统服务（launchd）

参考 `INSTALL.md` 中的 launchd 配置。

---

## ⚠️ 注意事项

### Cookie 过期

- Cookie 会过期（通常几天到几周）
- 如果爬虫失败，重新获取 Cookie 并更新配置文件
- 更新方法：重新编辑 `wechat_api_config.txt`

### Token 变化

- Token 可能会在重新登录后变化
- 如果报错，检查并更新 token

### 安全性

- `wechat_api_config.txt` 已加入 `.gitignore`
- **不要分享你的 token 和 cookie**
- 它们包含你的登录信息

---

## 📊 数据库查看

```bash
# 查看统计信息
python3 article_storage.py

# 查看所有文章
sqlite3 wechat_articles.db "SELECT title, publish_time FROM articles ORDER BY publish_time DESC LIMIT 10;"
```

---

## 🆘 故障排查

### 错误 1：Token 无效

```
✗ API 返回错误: invalid token
```

**解决**：重新获取 token 并更新配置文件

### 错误 2：Cookie 过期

```
✗ 请求失败: HTTP 401
```

**解决**：重新获取 cookie 并更新配置文件

### 错误 3：网络错误

```
✗ 网络请求错误: ...
```

**解决**：检查网络连接，稍后重试

---

## 🎯 完成！

现在你有了一个**完全自动化**的微信公众号爬虫：

✅ **实时**：无延迟，获取最新文章
✅ **完整**：不漏任何文章
✅ **稳定**：使用官方 API，不会被拦截
✅ **自动**：每周一自动运行，无需人工干预

**享受自动化带来的便利吧！** 🚀
