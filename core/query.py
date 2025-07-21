from typing import List

import numpy as np


def exp_to_level(exp: int) -> int:
    """
    根据经验值计算等级

    参数:
        exp: 用户当前经验值（负数记为0）

    返回:
        等级 (1-50)

    公式:
        L = min(50, 1 + 49 * (log(exp + 1) / log(exp_cap + 1))^gamma)
    """
    exp = max(exp, 0)  # 负数经验值记为0
    exp_cap = 50000  # 50级对应经验值
    gamma = 3.45  # 控制前快后慢的指数

    if exp == 0:
        return 1

    base = np.log(exp + 1) / np.log(exp_cap + 1)
    scaled = base**gamma
    level = 1 + 49 * scaled

    return min(50, int(level))


def batch_exp_to_level(exp_list: List[int]) -> List[int]:
    """
    批量计算经验值对应的等级

    参数:
        exp_list: 经验值列表

    返回:
        等级列表
    """
    return [exp_to_level(exp) for exp in exp_list]


def level_to_min_exp(level: int) -> int:
    """
    计算达到指定等级所需的最小经验值（反向计算）

    参数:
        level: 目标等级 (1-50)

    返回:
        所需最小经验值
    """
    if level <= 1:
        return 0
    if level >= 50:
        return 50000

    exp_cap = 50000
    gamma = 3.45

    # 反向计算：从等级推导经验值
    # level = 1 + 49 * scaled
    # scaled = (level - 1) / 49
    scaled = (level - 1) / 49

    # scaled = base^gamma
    # base = scaled^(1/gamma)
    base = scaled ** (1 / gamma)

    # base = log(exp + 1) / log(exp_cap + 1)
    # exp = exp(base * log(exp_cap + 1)) - 1
    exp = np.exp(base * np.log(exp_cap + 1)) - 1

    return int(exp)


def get_level_range(level: int) -> tuple:
    """
    获取指定等级的经验值范围

    参数:
        level: 等级

    返回:
        (min_exp, max_exp) 元组
    """
    min_exp = level_to_min_exp(level)
    max_exp = level_to_min_exp(level + 1) - 1 if level < 50 else float("inf")

    return (min_exp, max_exp)


def interactive_query():
    """
    交互式查询功能
    """
    print("=== 论坛等级查询系统 ===")
    print("输入 'q' 退出程序")

    while True:
        try:
            user_input = input("\n请输入经验值: ").strip()

            if user_input.lower() == "q":
                print("退出程序")
                break

            exp = int(user_input)
            level = exp_to_level(exp)
            min_exp, max_exp = get_level_range(level)

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

        except ValueError:
            print("请输入有效的数字！")
        except KeyboardInterrupt:
            print("\n程序被中断")
            break


if __name__ == "__main__":
    interactive_query()
