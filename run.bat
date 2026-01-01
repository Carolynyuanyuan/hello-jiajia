@echo off
chcp 65001 > nul
REM 微信公众号爬虫 - Windows 快速启动脚本

echo ======================================
echo   光储星球 - 微信公众号爬虫系统
echo ======================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
    echo.
)

REM 检查配置文件
if not exist "config.yaml" (
    echo 未找到 config.yaml，正在从示例文件创建...
    if exist "config.yaml.example" (
        copy config.yaml.example config.yaml >nul
        echo ✓ 已创建 config.yaml ^(默认监控：光储星球，每周一早上9点爬取^)
        echo.
    ) else (
        echo 错误: 未找到 config.yaml.example
        pause
        exit /b 1
    )
)

REM 显示菜单
echo 请选择操作:
echo 1) 立即爬取文章并生成周摘要（测试用）
echo 2) 启动定时调度器（每周一早上9点自动执行）
echo 3) 仅爬取文章
echo 4) 仅生成周摘要
echo 5) 退出
echo.
set /p choice="请输入选项 [1-5]: "

if "%choice%"=="1" (
    echo.
    echo 正在爬取文章并生成周摘要...
    python scheduler.py --run-now weekly
    echo.
    echo 完成！摘要文件保存在 digests\ 目录
    pause
) else if "%choice%"=="2" (
    echo.
    echo 启动定时调度器...
    echo 系统将在每周一早上9:00自动爬取文章并生成摘要
    echo 按 Ctrl+C 停止
    echo.
    python scheduler.py
) else if "%choice%"=="3" (
    echo.
    echo 正在爬取文章...
    python scheduler.py --run-now scrape
    pause
) else if "%choice%"=="4" (
    echo.
    echo 正在生成周摘要...
    python scheduler.py --run-now weekly
    echo.
    echo 完成！摘要文件保存在 digests\ 目录
    pause
) else if "%choice%"=="5" (
    echo 退出
    exit /b 0
) else (
    echo 无效选项
    pause
    exit /b 1
)
