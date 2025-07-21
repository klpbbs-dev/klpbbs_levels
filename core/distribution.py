import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from typing import Dict, List, Tuple
from .query import exp_to_level, batch_exp_to_level

# 设置中文字体支持
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False


def load_group_statistics(file_path: str) -> pd.DataFrame:
    """
    加载用户经验值分组统计数据

    参数:
        file_path: CSV文件路径

    返回:
        包含经验值分组和用户数量的DataFrame
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"加载数据文件失败: {e}")
        return None


def parse_exp_range(exp_group: str) -> Tuple[int, int]:
    """
    解析经验值范围字符串

    参数:
        exp_group: 经验值范围字符串，如 "0-9", "100-199"

    返回:
        (min_exp, max_exp) 元组
    """
    try:
        if "-" in exp_group:
            min_exp, max_exp = map(int, exp_group.split("-"))
            return min_exp, max_exp
        else:
            # 处理单个数值的情况
            exp = int(exp_group)
            return exp, exp
    except:
        return 0, 0


def calculate_level_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    根据经验值分组计算等级分布

    参数:
        df: 包含经验值分组统计的DataFrame

    返回:
        包含等级分布的DataFrame
    """
    level_distribution = {}

    for _, row in df.iterrows():
        exp_group = row["exp_group"]
        count = row["count"]

        min_exp, max_exp = parse_exp_range(exp_group)

        # 使用范围中点计算等级
        mid_exp = (min_exp + max_exp) // 2
        level = exp_to_level(mid_exp)

        if level in level_distribution:
            level_distribution[level] += count
        else:
            level_distribution[level] = count

    # 转换为DataFrame
    result_df = pd.DataFrame(
        [
            {"level": level, "user_count": count}
            for level, count in sorted(level_distribution.items())
        ]
    )

    # 计算百分比
    total_users = result_df["user_count"].sum()
    result_df["percentage"] = (result_df["user_count"] / total_users * 100).round(2)

    return result_df


def plot_exp_distribution(
    df: pd.DataFrame, save_path: str = None, show_plot: bool = True
):
    """
    绘制经验值分布图

    参数:
        df: 经验值分组统计DataFrame
        save_path: 保存路径
        show_plot: 是否显示图表
    """
    # 解析经验值范围并计算中点
    exp_midpoints = []
    counts = []
    labels = []

    for _, row in df.iterrows():
        exp_group = row["exp_group"]
        count = row["count"]

        min_exp, max_exp = parse_exp_range(exp_group)
        mid_exp = (min_exp + max_exp) // 2

        exp_midpoints.append(mid_exp)
        counts.append(count)
        labels.append(exp_group)

    plt.figure(figsize=(15, 8))

    # 使用对数刻度显示用户数量
    plt.subplot(2, 1, 1)
    bars = plt.bar(range(len(exp_midpoints)), counts, color="#3A86FF", alpha=0.7)
    plt.xlabel("经验值范围", fontsize=12)
    plt.ylabel("用户数量 (对数刻度)", fontsize=12)
    plt.title("用户经验值分布（原始数据）", fontsize=14, fontweight="bold")
    plt.yscale("log")
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.grid(True, alpha=0.3, axis="y")

    # 标注最高的几个柱子
    top_indices = np.argsort(counts)[-5:]
    for i in top_indices:
        plt.annotate(
            f"{counts[i]:,}",
            xy=(i, counts[i]),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            fontsize=8,
        )

    # 绘制累积分布
    plt.subplot(2, 1, 2)
    cumulative_counts = np.cumsum(counts)
    total_users = cumulative_counts[-1]
    cumulative_percentage = (cumulative_counts / total_users) * 100

    plt.plot(
        range(len(exp_midpoints)),
        cumulative_percentage,
        marker="o",
        linewidth=2,
        color="#F18F01",
        markersize=4,
    )
    plt.xlabel("经验值范围", fontsize=12)
    plt.ylabel("累积用户百分比 (%)", fontsize=12)
    plt.title("用户经验值累积分布", fontsize=14, fontweight="bold")
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)

    # 标注关键百分位点
    percentiles = [50, 80, 90, 95, 99]
    for p in percentiles:
        idx = np.searchsorted(cumulative_percentage, p)
        if idx < len(exp_midpoints):
            plt.axhline(y=p, color="red", linestyle="--", alpha=0.5)
            plt.annotate(
                f"{p}%",
                xy=(len(exp_midpoints) - 1, p),
                xytext=(5, 0),
                textcoords="offset points",
                fontsize=8,
                color="red",
            )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"经验值分布图已保存到: {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_level_distribution(
    level_df: pd.DataFrame, save_path: str = None, show_plot: bool = True
):
    """
    绘制等级分布图

    参数:
        level_df: 等级分布DataFrame
        save_path: 保存路径
        show_plot: 是否显示图表
    """
    plt.figure(figsize=(15, 10))

    # 等级分布柱状图
    plt.subplot(2, 2, 1)
    bars = plt.bar(
        level_df["level"],
        level_df["user_count"],
        color="#2E86AB",
        alpha=0.7,
        edgecolor="black",
    )
    plt.xlabel("等级", fontsize=12)
    plt.ylabel("用户数量", fontsize=12)
    plt.title("用户等级分布", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3, axis="y")

    # 标注用户数量最多的等级
    max_idx = level_df["user_count"].idxmax()
    max_level = level_df.loc[max_idx, "level"]
    max_count = level_df.loc[max_idx, "user_count"]
    plt.annotate(
        f"最多: {max_count:,}人",
        xy=(max_level, max_count),
        xytext=(10, 10),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
        arrowprops=dict(arrowstyle="->", color="red"),
    )

    # 等级分布百分比饼图（只显示前10个等级）
    plt.subplot(2, 2, 2)
    top_levels = level_df.nlargest(10, "user_count")
    other_count = level_df["user_count"].sum() - top_levels["user_count"].sum()

    pie_data = list(top_levels["user_count"])
    pie_labels = [f"等级{level}" for level in top_levels["level"]]

    if other_count > 0:
        pie_data.append(other_count)
        pie_labels.append("其他等级")

    plt.pie(pie_data, labels=pie_labels, autopct="%1.1f%%", startangle=90)
    plt.title("等级分布占比（Top 10）", fontsize=14, fontweight="bold")

    # 累积分布曲线
    plt.subplot(2, 2, 3)
    cumulative_users = level_df["user_count"].cumsum()
    total_users = level_df["user_count"].sum()
    cumulative_percentage = (cumulative_users / total_users) * 100

    plt.plot(
        level_df["level"],
        cumulative_percentage,
        marker="o",
        linewidth=2,
        color="#C73E1D",
        markersize=4,
    )
    plt.xlabel("等级", fontsize=12)
    plt.ylabel("累积用户百分比 (%)", fontsize=12)
    plt.title("等级累积分布", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)

    # 标注关键等级点
    key_levels = [10, 20, 30, 40]
    for level in key_levels:
        if level in level_df["level"].values:
            idx = level_df[level_df["level"] == level].index[0]
            percentage = cumulative_percentage.iloc[idx]
            plt.axvline(x=level, color="red", linestyle="--", alpha=0.5)
            plt.annotate(
                f"{level}级\n{percentage:.1f}%",
                xy=(level, percentage),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                color="red",
            )

    # 等级分布统计表
    plt.subplot(2, 2, 4)
    plt.axis("off")

    # 计算关键统计数据
    stats_text = f"""
等级分布统计:

总用户数: {total_users:,}
平均等级: {(level_df['level'] * level_df['user_count']).sum() / total_users:.2f}
中位数等级: {level_df.loc[cumulative_percentage >= 50, 'level'].iloc[0] if len(level_df.loc[cumulative_percentage >= 50]) > 0 else 'N/A'}

等级分布:
1-10级: {level_df[level_df['level'] <= 10]['user_count'].sum():,} ({level_df[level_df['level'] <= 10]['user_count'].sum()/total_users*100:.1f}%)
11-20级: {level_df[(level_df['level'] > 10) & (level_df['level'] <= 20)]['user_count'].sum():,} ({level_df[(level_df['level'] > 10) & (level_df['level'] <= 20)]['user_count'].sum()/total_users*100:.1f}%)
21-30级: {level_df[(level_df['level'] > 20) & (level_df['level'] <= 30)]['user_count'].sum():,} ({level_df[(level_df['level'] > 20) & (level_df['level'] <= 30)]['user_count'].sum()/total_users*100:.1f}%)
31-40级: {level_df[(level_df['level'] > 30) & (level_df['level'] <= 40)]['user_count'].sum():,} ({level_df[(level_df['level'] > 30) & (level_df['level'] <= 40)]['user_count'].sum()/total_users*100:.1f}%)
41-50级: {level_df[level_df['level'] > 40]['user_count'].sum():,} ({level_df[level_df['level'] > 40]['user_count'].sum()/total_users*100:.1f}%)
"""

    plt.text(
        0.1,
        0.9,
        stats_text,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
    )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"等级分布图已保存到: {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def analyze_distribution(file_path: str) -> Dict:
    """
    分析用户经验值和等级分布

    参数:
        file_path: group_statistics.csv文件路径

    返回:
        分析结果字典
    """
    df = load_group_statistics(file_path)
    if df is None:
        return None

    # 计算等级分布
    level_df = calculate_level_distribution(df)

    # 计算总用户数
    total_users = df["count"].sum()

    # 计算关键统计数据
    analysis = {
        "total_users": total_users,
        "exp_distribution": df,
        "level_distribution": level_df,
        "avg_level": (level_df["level"] * level_df["user_count"]).sum() / total_users,
        "users_below_level_40": level_df[level_df["level"] < 40]["user_count"].sum(),
        "percentage_below_level_40": level_df[level_df["level"] < 40][
            "user_count"
        ].sum()
        / total_users
        * 100,
    }

    return analysis


def generate_distribution_report(
    file_path: str, output_dir: str = ".", show_plots: bool = False
):
    """
    生成完整的分布分析报告

    参数:
        file_path: group_statistics.csv文件路径
        output_dir: 输出目录
        show_plots: 是否显示图表
    """
    import os

    analysis = analyze_distribution(file_path)
    if analysis is None:
        print("分析失败：无法加载数据文件")
        return

    # 创建子目录
    charts_dir = os.path.join(output_dir, "charts")
    reports_dir = os.path.join(output_dir, "reports")
    os.makedirs(charts_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    # 生成图表
    exp_dist_path = os.path.join(charts_dir, "exp_distribution.png")
    level_dist_path = os.path.join(charts_dir, "level_distribution.png")

    plot_exp_distribution(analysis["exp_distribution"], exp_dist_path, show_plots)
    plot_level_distribution(analysis["level_distribution"], level_dist_path, show_plots)

    # 保存分析结果
    level_dist_csv = os.path.join(reports_dir, "level_distribution.csv")
    analysis["level_distribution"].to_csv(level_dist_csv, index=False, encoding="utf-8")

    # 生成文本报告
    report_path = os.path.join(reports_dir, "distribution_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== 论坛用户等级分布分析报告 ===\n\n")
        f.write(f"总用户数: {analysis['total_users']:,}\n")
        f.write(f"平均等级: {analysis['avg_level']:.2f}\n")
        f.write(
            f"40级以下用户: {analysis['users_below_level_40']:,} ({analysis['percentage_below_level_40']:.1f}%)\n\n"
        )

        f.write("等级分布详情:\n")
        for _, row in analysis["level_distribution"].iterrows():
            f.write(
                f"等级 {int(row['level']):2d}: {row['user_count']:8,} 人 ({row['percentage']:5.2f}%)\n"
            )

    print(f"分布分析报告已生成到: {reports_dir}")
    print(f"- 经验值分布图: {exp_dist_path}")
    print(f"- 等级分布图: {level_dist_path}")
    print(f"- 等级分布数据: {level_dist_csv}")
    print(f"- 分析报告: {report_path}")


if __name__ == "__main__":
    # 示例用法
    file_path = "../datas/group_statistics.csv"
    generate_distribution_report(file_path, show_plots=True)
