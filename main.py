#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论坛等级系统主程序

功能模块:
- 查询模块: 经验值 → 等级转换
- 图表模块: 等级曲线绘制
- 分布模块: 用户分布分析
- SQL模块: 数据库迁移脚本生成
"""

import sys
import os
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.query import (
    exp_to_level,
    interactive_query,
    get_level_range,
    level_to_min_exp,
)
from core.chart import generate_all_charts, plot_level_curve
from core.distribution import generate_distribution_report, analyze_distribution
from core.sql_generator import generate_all_sql_scripts


def print_banner():
    """
    打印程序横幅
    """
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    论坛等级系统工具                          ║
║                  Forum Level System Tool                     ║
╠══════════════════════════════════════════════════════════════╣
║  功能模块:                                                   ║
║  • 查询模块: 经验值 ↔ 等级转换                               ║
║  • 图表模块: 等级曲线可视化                                  ║
║  • 分布模块: 用户分布分析                                    ║
║  • SQL模块: 数据库迁移脚本                                   ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_query(args):
    """
    查询命令处理
    """
    if args.interactive:
        interactive_query()
    elif args.exp is not None:
        exp = args.exp
        level = exp_to_level(exp)
        min_exp, max_exp = get_level_range(level)

        print(f"\n=== 查询结果 ===")
        print(f"经验值: {exp}")
        print(f"等级: {level}")
        print(
            f"当前等级范围: {min_exp} - {max_exp if max_exp != float('inf') else '∞'}"
        )

        if level < 50:
            next_level_min = level_to_min_exp(level + 1)
            remaining_exp = next_level_min - exp
            print(f"距离下一级还需: {remaining_exp} 经验值")
        else:
            print("已达到最高等级！")
    elif args.level is not None:
        level = args.level
        if 1 <= level <= 50:
            min_exp = level_to_min_exp(level)
            max_exp = level_to_min_exp(level + 1) - 1 if level < 50 else float("inf")
            print(f"\n=== 查询结果 ===")
            print(f"等级: {level}")
            print(f"所需最小经验值: {min_exp}")
            print(
                f"等级范围: {min_exp} - {max_exp if max_exp != float('inf') else '∞'}"
            )
        else:
            print("错误: 等级必须在1-50之间")
    else:
        print("请指定 --exp 或 --level 参数，或使用 --interactive 进入交互模式")


def cmd_chart(args):
    """
    图表命令处理
    """
    output_dir = args.output or "output"
    os.makedirs(output_dir, exist_ok=True)

    if args.all:
        print("生成所有图表...")
        generate_all_charts(output_dir, args.show)
    elif args.curve:
        print("生成等级曲线图...")
        charts_dir = os.path.join(output_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        save_path = os.path.join(charts_dir, "level_curve.png")
        plot_level_curve(args.max_exp, save_path, args.show)
    else:
        print("请指定要生成的图表类型 (--curve, --all)")


def cmd_distribution(args):
    """
    分布分析命令处理
    """
    data_file = args.file or "datas/group_statistics.csv"
    output_dir = args.output or "output"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(data_file):
        print(f"错误: 数据文件不存在: {data_file}")
        return

    print(f"分析数据文件: {data_file}")
    generate_distribution_report(data_file, output_dir, args.show)


def cmd_sql(args):
    """
    SQL脚本生成命令处理
    """
    output_dir = args.output or "output"
    os.makedirs(output_dir, exist_ok=True)
    table_name = args.table or "users"

    print(f"生成SQL迁移脚本 (表名: {table_name})...")
    generate_all_sql_scripts(table_name, output_dir)


def cmd_demo(args):
    """
    演示命令处理
    """
    print("=== 论坛等级系统演示 ===")
    output_dir = args.output or "output"
    os.makedirs(output_dir, exist_ok=True)

    # 演示查询功能
    print("\n1. 查询功能演示:")
    test_exp_values = [0, 10, 50, 100, 500, 1000, 5000, 10000, 25000, 50000]
    print("EXP\t\tLevel")
    print("-" * 20)
    for exp in test_exp_values:
        level = exp_to_level(exp)
        print(f"{exp}\t\t{level}")

    # 生成图表
    print("\n2. 生成图表...")
    generate_all_charts(output_dir, False)

    # 生成SQL脚本
    print("\n3. 生成SQL脚本...")
    generate_all_sql_scripts("users", output_dir)

    # 分析分布（如果数据文件存在）
    data_file = "datas/group_statistics.csv"
    if os.path.exists(data_file):
        print("\n4. 分析用户分布...")
        generate_distribution_report(data_file, output_dir, False)
    else:
        print(f"\n4. 跳过分布分析 (数据文件不存在: {data_file})")

    print(f"\n演示完成！所有文件已生成到: {output_dir}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="论坛等级系统工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py query --exp 1000                    # 查询经验值1000对应的等级
  python main.py query --level 20                    # 查询等级20所需的经验值
  python main.py query --interactive                 # 交互式查询
  python main.py chart --curve --show                # 生成并显示等级曲线图
  python main.py chart --all --output ./charts       # 生成所有图表到指定目录
  python main.py distribution --show                 # 分析用户分布并显示图表
  python main.py sql --table users --output ./sql    # 生成SQL脚本
  python main.py demo                                # 运行完整演示
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 查询命令
    query_parser = subparsers.add_parser("query", help="经验值和等级查询")
    query_group = query_parser.add_mutually_exclusive_group()
    query_group.add_argument("--exp", type=int, help="查询经验值对应的等级")
    query_group.add_argument("--level", type=int, help="查询等级所需的经验值")
    query_group.add_argument(
        "--interactive", action="store_true", help="交互式查询模式"
    )

    # 图表命令
    chart_parser = subparsers.add_parser("chart", help="生成图表")
    chart_parser.add_argument("--curve", action="store_true", help="生成等级曲线图")
    chart_parser.add_argument("--all", action="store_true", help="生成所有图表")
    chart_parser.add_argument(
        "--max-exp", type=int, default=50000, help="最大经验值 (默认: 50000)"
    )
    chart_parser.add_argument("--show", action="store_true", help="显示图表")
    chart_parser.add_argument("--output", help="输出目录 (默认: 当前目录)")

    # 分布分析命令
    dist_parser = subparsers.add_parser("distribution", help="用户分布分析")
    dist_parser.add_argument(
        "--file", help="数据文件路径 (默认: datas/group_statistics.csv)"
    )
    dist_parser.add_argument("--show", action="store_true", help="显示图表")
    dist_parser.add_argument("--output", help="输出目录 (默认: 当前目录)")

    # SQL脚本命令
    sql_parser = subparsers.add_parser("sql", help="生成SQL迁移脚本")
    sql_parser.add_argument("--table", default="users", help="用户表名 (默认: users)")
    sql_parser.add_argument("--output", help="输出目录 (默认: 当前目录)")

    # 演示命令
    demo_parser = subparsers.add_parser("demo", help="运行完整演示")
    demo_parser.add_argument("--output", help="输出目录 (默认: 当前目录)")

    args = parser.parse_args()

    # 如果没有指定命令，显示帮助
    if not args.command:
        print_banner()
        parser.print_help()
        return

    # 执行对应的命令
    try:
        if args.command == "query":
            cmd_query(args)
        elif args.command == "chart":
            cmd_chart(args)
        elif args.command == "distribution":
            cmd_distribution(args)
        elif args.command == "sql":
            cmd_sql(args)
        elif args.command == "demo":
            cmd_demo(args)
        else:
            print(f"未知命令: {args.command}")
            parser.print_help()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"错误: {e}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
