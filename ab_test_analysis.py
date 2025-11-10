#!/usr/bin/env python3
"""
A/B测试统计显著性分析
分析halloween-sale实验数据（移除vs保留"learn more"按钮）
"""

import numpy as np
from scipy import stats
import pandas as pd

def chi_square_test(conversions_a, total_a, conversions_b, total_b, metric_name):
    """
    卡方检验用于比较两个比例
    """
    # 构建列联表
    observed = np.array([
        [conversions_a, total_a - conversions_a],
        [conversions_b, total_b - conversions_b]
    ])

    chi2, p_value, dof, expected = stats.chi2_contingency(observed)

    rate_a = conversions_a / total_a * 100
    rate_b = conversions_b / total_b * 100
    diff = rate_a - rate_b

    return {
        'metric': metric_name,
        'rate_a': rate_a,
        'rate_b': rate_b,
        'difference': diff,
        'chi2': chi2,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

def proportion_z_test(conversions_a, total_a, conversions_b, total_b, metric_name):
    """
    双样本比例Z检验
    """
    p_a = conversions_a / total_a
    p_b = conversions_b / total_b
    p_pool = (conversions_a + conversions_b) / (total_a + total_b)

    se = np.sqrt(p_pool * (1 - p_pool) * (1/total_a + 1/total_b))
    z_score = (p_a - p_b) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

    return {
        'metric': metric_name,
        'rate_a': p_a * 100,
        'rate_b': p_b * 100,
        'difference': (p_a - p_b) * 100,
        'z_score': z_score,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

def welch_t_test(mean_a, n_a, mean_b, n_b, metric_name):
    """
    使用Welch's t-test比较两个均值
    由于没有标准差，我们假设一个合理的变异系数(CV)
    """
    # 假设变异系数(CV) = 0.8，这是会话时长的合理假设
    cv = 0.8
    std_a = mean_a * cv
    std_b = mean_b * cv

    # Welch's t-test
    t_stat = (mean_a - mean_b) / np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))

    # 自由度计算（Welch-Satterthwaite公式）
    df = ((std_a**2 / n_a) + (std_b**2 / n_b))**2 / \
         ((std_a**2 / n_a)**2 / (n_a - 1) + (std_b**2 / n_b)**2 / (n_b - 1))

    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

    diff_pct = ((mean_a - mean_b) / mean_b) * 100

    return {
        'metric': metric_name,
        'mean_a': mean_a,
        'mean_b': mean_b,
        'difference': mean_a - mean_b,
        'difference_pct': diff_pct,
        't_stat': t_stat,
        'p_value': p_value,
        'df': df,
        'significant': p_value < 0.05
    }

def print_results(results, title):
    """打印格式化的结果"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

    for result in results:
        print(f"\n{result['metric']}:")
        print(f"  版本A: {result.get('rate_a', result.get('mean_a')):.2f}")
        print(f"  版本B: {result.get('rate_b', result.get('mean_b')):.2f}")
        print(f"  差异: {result['difference']:.2f}" +
              (f" ({result['difference_pct']:.2f}%)" if 'difference_pct' in result else ""))

        if 'z_score' in result:
            print(f"  Z得分: {result['z_score']:.4f}")
        elif 't_stat' in result:
            print(f"  t统计量: {result['t_stat']:.4f}")
            print(f"  自由度: {result['df']:.2f}")
        elif 'chi2' in result:
            print(f"  卡方值: {result['chi2']:.4f}")

        print(f"  p值: {result['p_value']:.4f}")
        print(f"  统计显著性(α=0.05): {'✓ 显著' if result['significant'] else '✗ 不显著'}")

        if result['p_value'] < 0.001:
            print(f"  显著性水平: p < 0.001 (极其显著)")
        elif result['p_value'] < 0.01:
            print(f"  显著性水平: p < 0.01 (非常显著)")
        elif result['p_value'] < 0.05:
            print(f"  显著性水平: p < 0.05 (显著)")
        elif result['p_value'] < 0.1:
            print(f"  显著性水平: 0.05 < p < 0.1 (边缘显著)")

def main():
    print("A/B测试统计分析报告")
    print("实验：halloween-sale (移除learn more) vs halloween-sales (保留learn more)")
    print(f"分析日期: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ==================== 整体数据分析 ====================

    # 版本A: halloween-sale (移除learn more)
    total_sessions_a = 2714
    avg_duration_a = 128
    bounce_rate_a = 0.247
    bounces_a = int(total_sessions_a * bounce_rate_a)

    # 版本B: halloween-sales (保留learn more，控制组)
    total_sessions_b = 2506
    avg_duration_b = 114
    bounce_rate_b = 0.251
    bounces_b = int(total_sessions_b * bounce_rate_b)

    # 跳出率检验
    bounce_result = proportion_z_test(
        bounces_a, total_sessions_a,
        bounces_b, total_sessions_b,
        "整体跳出率"
    )

    # 会话时长检验
    duration_result = welch_t_test(
        avg_duration_a, total_sessions_a,
        avg_duration_b, total_sessions_b,
        "平均会话时长(秒)"
    )

    print_results([bounce_result, duration_result], "整体数据分析")

    # ==================== 按设备类型分析 ====================

    # 手机数据
    mobile_a = {'sessions': 1919, 'duration': 124, 'bounce_rate': 0.281}
    mobile_b = {'sessions': 1760, 'duration': 109, 'bounce_rate': 0.283}

    mobile_bounce = proportion_z_test(
        int(mobile_a['sessions'] * mobile_a['bounce_rate']), mobile_a['sessions'],
        int(mobile_b['sessions'] * mobile_b['bounce_rate']), mobile_b['sessions'],
        "手机 - 跳出率"
    )

    mobile_duration = welch_t_test(
        mobile_a['duration'], mobile_a['sessions'],
        mobile_b['duration'], mobile_b['sessions'],
        "手机 - 平均会话时长(秒)"
    )

    # 电脑数据
    desktop_a = {'sessions': 645, 'duration': 136, 'bounce_rate': 0.144}
    desktop_b = {'sessions': 584, 'duration': 132, 'bounce_rate': 0.13}

    desktop_bounce = proportion_z_test(
        int(desktop_a['sessions'] * desktop_a['bounce_rate']), desktop_a['sessions'],
        int(desktop_b['sessions'] * desktop_b['bounce_rate']), desktop_b['sessions'],
        "电脑 - 跳出率"
    )

    desktop_duration = welch_t_test(
        desktop_a['duration'], desktop_a['sessions'],
        desktop_b['duration'], desktop_b['sessions'],
        "电脑 - 平均会话时长(秒)"
    )

    # 平板数据
    tablet_a = {'sessions': 150, 'duration': 152, 'bounce_rate': 0.253}
    tablet_b = {'sessions': 162, 'duration': 98, 'bounce_rate': 0.389}

    tablet_bounce = proportion_z_test(
        int(tablet_a['sessions'] * tablet_a['bounce_rate']), tablet_a['sessions'],
        int(tablet_b['sessions'] * tablet_b['bounce_rate']), tablet_b['sessions'],
        "平板 - 跳出率"
    )

    tablet_duration = welch_t_test(
        tablet_a['duration'], tablet_a['sessions'],
        tablet_b['duration'], tablet_b['sessions'],
        "平板 - 平均会话时长(秒)"
    )

    print_results([mobile_bounce, mobile_duration], "手机设备分析")
    print_results([desktop_bounce, desktop_duration], "电脑设备分析")
    print_results([tablet_bounce, tablet_duration], "平板设备分析")

    # ==================== 综合总结 ====================

    print(f"\n{'='*80}")
    print("综合结论")
    print(f"{'='*80}\n")

    results_summary = [
        ("整体跳出率", bounce_result),
        ("整体会话时长", duration_result),
        ("手机跳出率", mobile_bounce),
        ("手机会话时长", mobile_duration),
        ("电脑跳出率", desktop_bounce),
        ("电脑会话时长", desktop_duration),
        ("平板跳出率", tablet_bounce),
        ("平板会话时长", tablet_duration)
    ]

    significant_count = sum(1 for _, r in results_summary if r['significant'])

    print(f"总计检验指标: {len(results_summary)}")
    print(f"统计显著的指标: {significant_count}")
    print(f"不显著的指标: {len(results_summary) - significant_count}\n")

    print("显著差异详情:")
    for name, result in results_summary:
        if result['significant']:
            direction = "↑" if result['difference'] > 0 else "↓"
            print(f"  ✓ {name}: 版本A {direction} (p={result['p_value']:.4f})")

    print("\n不显著差异:")
    for name, result in results_summary:
        if not result['significant']:
            print(f"  ✗ {name}: 无显著差异 (p={result['p_value']:.4f})")

    print("\n实验建议:")
    if duration_result['significant']:
        print(f"  • 会话时长有显著提升({duration_result['difference_pct']:.1f}%)，移除'learn more'按钮效果积极")

    if bounce_result['significant']:
        print(f"  • 跳出率{'降低' if bounce_result['difference'] < 0 else '升高'}显著")
    else:
        print(f"  • 整体跳出率无显著差异，两个版本在用户留存方面表现相当")

    # 检查设备特定的效果
    if tablet_duration['significant'] or tablet_bounce['significant']:
        print(f"  • 平板设备显示出显著差异，建议针对平板用户进行进一步优化")

    print("\n注意事项:")
    print("  • 会话时长分析基于假设的变异系数(CV=0.8)")
    print("  • 实际标准差可能影响t检验的结果")
    print("  • 建议结合业务指标(转化率、收入等)综合评估")
    print("  • 平板设备样本量较小，结果需谨慎解读")

if __name__ == "__main__":
    main()
