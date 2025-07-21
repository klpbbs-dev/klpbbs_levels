import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from .query import exp_to_level

# 设置中文字体支持
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False


def plot_level_curve(
    max_exp: int = 50000, save_path: str = None, show_plot: bool = True
):
    """
    绘制经验值-等级曲线图

    参数:
        max_exp: 最大经验值
        save_path: 保存路径，如果为None则不保存
        show_plot: 是否显示图表
    """
    exp_values = np.linspace(0, max_exp, 1000)
    levels = [exp_to_level(int(exp)) for exp in exp_values]

    plt.figure(figsize=(12, 8))
    plt.plot(exp_values, levels, linewidth=2, color="#2E86AB", label="等级曲线")
    plt.xlabel("经验值 (EXP)", fontsize=12)
    plt.ylabel("等级 (Level)", fontsize=12)
    plt.title("论坛等级系统：经验值 → 等级曲线", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_exp)
    plt.ylim(1, max(50, 6))  # 确保能显示旧系统的最高等级
    plt.legend()

    # 添加关键节点标注
    key_exp_values = [0, 500, 1000, 5000, 10000, 25000, 50000]

    for exp in key_exp_values:
        if exp <= max_exp:
            level = exp_to_level(exp)
            plt.scatter(exp, level, color="red", s=50, zorder=5)
            plt.annotate(
                f"({exp}, {level})",
                xy=(exp, level),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"等级曲线图已保存到: {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def old_exp_to_level(exp: int) -> int:
    """
    旧等级系统的经验值到等级转换

    旧等级数据:
    等级 1: 0 经验值
    等级 2: 200 经验值
    等级 3: 1000 经验值
    等级 4: 5000 经验值
    等级 5: 10000 经验值
    等级 6: 50000 经验值
    """
    if exp < 0:
        return 1
    elif exp < 200:
        return 1
    elif exp < 1000:
        return 2
    elif exp < 5000:
        return 3
    elif exp < 10000:
        return 4
    elif exp < 50000:
        return 5
    else:
        return 6


def plot_level_comparison(
    max_exp: int = 50000, save_path: str = None, show_plot: bool = True
):
    """
    绘制新旧等级系统对比图

    参数:
        max_exp: 最大经验值
        save_path: 保存路径
        show_plot: 是否显示图表
    """
    exp_values = np.linspace(0, max_exp, 1000)
    new_levels = [exp_to_level(int(exp)) for exp in exp_values]
    # 使用真实的旧等级系统数据
    old_levels = [old_exp_to_level(int(exp)) for exp in exp_values]

    plt.figure(figsize=(12, 8))
    plt.plot(exp_values, new_levels, linewidth=2, color="#2E86AB", label="新等级系统")
    plt.plot(
        exp_values,
        old_levels,
        linewidth=2,
        color="#F18F01",
        linestyle="--",
        label="旧等级系统（1-6级）",
    )

    # 标注旧等级系统的关键节点
    old_key_points = [(0, 1), (200, 2), (1000, 3), (5000, 4), (10000, 5), (50000, 6)]
    for exp, level in old_key_points:
        if exp <= max_exp:
            plt.scatter(exp, level, color="orange", s=80, zorder=5, marker="s")
            plt.annotate(
                f"旧{level}级\n{exp}exp",
                xy=(exp, level),
                xytext=(10, -20),
                textcoords="offset points",
                fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.7),
            )

    plt.xlabel("经验值 (EXP)", fontsize=12)
    plt.ylabel("等级 (Level)", fontsize=12)
    plt.title("等级系统对比：新 vs 旧", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_exp)
    plt.ylim(1, 50)
    plt.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"等级对比图已保存到: {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_level_growth_rate(
    max_exp: int = 50000, save_path: str = None, show_plot: bool = True
):
    """
    绘制等级增长率图（显示升级难度变化）

    参数:
        max_exp: 最大经验值
        save_path: 保存路径
        show_plot: 是否显示图表
    """
    exp_values = np.linspace(1, max_exp, 1000)
    levels = [exp_to_level(int(exp)) for exp in exp_values]

    # 计算增长率（导数近似）
    growth_rates = []
    for i in range(1, len(levels)):
        rate = (levels[i] - levels[i - 1]) / (exp_values[i] - exp_values[i - 1])
        growth_rates.append(rate)

    plt.figure(figsize=(12, 8))
    plt.plot(exp_values[1:], growth_rates, linewidth=2, color="#C73E1D")
    plt.xlabel("经验值 (EXP)", fontsize=12)
    plt.ylabel("等级增长率 (Level/EXP)", fontsize=12)
    plt.title("等级增长率变化图（升级难度）", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_exp)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"等级增长率图已保存到: {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_exp_requirements(save_path: str = None, show_plot: bool = True):
    """
    绘制各等级所需经验值图

    参数:
        save_path: 保存路径
        show_plot: 是否显示图表
    """
    from .query import level_to_min_exp

    levels = list(range(1, 51))
    exp_requirements = [level_to_min_exp(level) for level in levels]

    plt.figure(figsize=(12, 8))
    plt.bar(levels, exp_requirements, color="#3A86FF", alpha=0.7, edgecolor="black")
    plt.xlabel("等级 (Level)", fontsize=12)
    plt.ylabel("所需最小经验值 (EXP)", fontsize=12)
    plt.title("各等级所需经验值", fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3, axis="y")
    plt.xlim(0, 51)

    # 标注关键等级
    key_levels = [1, 10, 20, 30, 40, 50]
    for level in key_levels:
        if level <= 50:
            exp = exp_requirements[level - 1]
            plt.annotate(
                f"{exp}",
                xy=(level, exp),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"经验值需求图已保存到: {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close()


def generate_all_charts(output_dir: str = ".", show_plots: bool = False):
    """
    生成所有图表

    参数:
        output_dir: 输出目录
        show_plots: 是否显示图表
    """
    import os

    # 创建charts子目录
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    charts = [
        (
            "level_curve.png",
            lambda: plot_level_curve(
                save_path=os.path.join(charts_dir, "level_curve.png"),
                show_plot=show_plots,
            ),
        ),
        (
            "level_comparison.png",
            lambda: plot_level_comparison(
                save_path=os.path.join(charts_dir, "level_comparison.png"),
                show_plot=show_plots,
            ),
        ),
        (
            "level_growth_rate.png",
            lambda: plot_level_growth_rate(
                save_path=os.path.join(charts_dir, "level_growth_rate.png"),
                show_plot=show_plots,
            ),
        ),
        (
            "exp_requirements.png",
            lambda: plot_exp_requirements(
                save_path=os.path.join(charts_dir, "exp_requirements.png"),
                show_plot=show_plots,
            ),
        ),
    ]

    for chart_name, chart_func in charts:
        try:
            chart_func()
        except Exception as e:
            print(f"生成 {chart_name} 时出错: {e}")

    print(f"所有图表已生成到: {charts_dir}")


if __name__ == "__main__":
    # 生成所有图表
    generate_all_charts(show_plots=True)
