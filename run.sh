#!/bin/bash
# 微信公众号爬虫 - 快速启动脚本

echo "======================================"
echo "  光储星球 - 微信公众号爬虫系统"
echo "======================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    echo "请先安装 Python 3: https://www.python.org/downloads/"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import requests" &> /dev/null; then
    echo "检测到缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
    echo ""
fi

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "未找到 config.yaml，正在从示例文件创建..."
    if [ -f "config.yaml.example" ]; then
        cp config.yaml.example config.yaml
        echo "✓ 已创建 config.yaml (默认监控：光储星球，每周一早上9点爬取)"
        echo ""
    else
        echo "错误: 未找到 config.yaml.example"
        exit 1
    fi
fi

# 显示菜单
echo "请选择操作:"
echo "1) 立即爬取文章并生成周摘要（测试用）"
echo "2) 启动定时调度器（每周一早上9点自动执行）"
echo "3) 仅爬取文章"
echo "4) 仅生成周摘要"
echo "5) 退出"
echo ""
read -p "请输入选项 [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "正在爬取文章并生成周摘要..."
        python3 scheduler.py --run-now weekly
        echo ""
        echo "完成！摘要文件保存在 digests/ 目录"
        ;;
    2)
        echo ""
        echo "启动定时调度器..."
        echo "系统将在每周一早上9:00自动爬取文章并生成摘要"
        echo "按 Ctrl+C 停止"
        echo ""
        python3 scheduler.py
        ;;
    3)
        echo ""
        echo "正在爬取文章..."
        python3 scheduler.py --run-now scrape
        ;;
    4)
        echo ""
        echo "正在生成周摘要..."
        python3 scheduler.py --run-now weekly
        echo ""
        echo "完成！摘要文件保存在 digests/ 目录"
        ;;
    5)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
