# 论坛等级系统工具

这是一个用于生成论坛等级系统相关数据的工具，包括等级曲线、经验要求、数据分布报告和数据库迁移脚本等。

## 用法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 生成所有数据

运行 `demo` 命令可以一键生成所有图表、报告和 SQL 脚本到 `output` 目录下。

```bash
python main.py demo
```

### 3. 单独生成特定数据

你也可以根据需要单独生成某一部分数据：

*   **生成图表:**
    ```bash
    python main.py chart
    ```
*   **生成数据分布报告:**
    ```bash
    python main.py distribution
    ```
*   **生成 SQL 迁移脚本:**
    ```bash
    python main.py sql
    ```

默认输出目录为 `output`，你可以通过 `--output` 参数指定其他目录。

## 核心算法：等级函数推导

### 目标

*   等级范围：$L \in [1, 50]$
*   经验值 $\text{exp} = 25,000$ 时，等级 $L = 40$
*   经验值 $\text{exp} = 50,000$ 时，等级 $L = 50$
*   等级随经验值的增长呈现先快后慢的趋势。

### 函数结构

为了满足上述要求，我们设计了如下函数结构。等级 $L$ 的计算方式为：

$$ L = \min \left(50,\; 1 + 49 \times f(\text{exp}) \right) $$

其中，$f(\text{exp})$ 是一个归一化的函数，其值域为 $[0, 1]$，并带有一个调节曲线形状的参数 $\gamma$：

$$ f(\text{exp}) = \left( \frac{\ln(\text{exp} + 1)}{\ln(\text{exp}_{\text{cap}} + 1)} \right)^{\gamma} $$

这里，$\text{exp}_{\text{cap}}$ 是达到满级（50级）所需的经验值，即 $50,000$。

### 参数求解

我们需要根据约束条件（$\text{exp} = 25,000$ 时 $L = 40$）来求解参数 $\gamma$。

将约束条件代入公式：

$$ 40 = 1 + 49 \times \left( \frac{\ln(25000 + 1)}{\ln(50000 + 1)} \right)^{\gamma} $$

为了方便计算，我们进行如下变换：

$$ \frac{40 - 1}{49} = \left( \frac{\ln(25001)}{\ln(50001)} \right)^{\gamma} $$

设：

$$ t = \frac{39}{49} \approx 0.7959 $$

$$ r = \frac{\ln(25001)}{\ln(50001)} $$

则方程变为：

$$ t = r^{\gamma} $$

两边取自然对数，解出 $\gamma$：

$$ \ln(t) = \gamma \ln(r) \implies \gamma = \frac{\ln(t)}{\ln(r)} $$

代入具体数值：

*   $\ln(25001) \approx 10.1266$
*   $\ln(50001) \approx 10.8198$
*   $r \approx \frac{10.1266}{10.8198} \approx 0.9360$
*   $\ln(t) = \ln(0.7959) \approx -0.2284$
*   $\ln(r) = \ln(0.9360) \approx -0.0662$

最终得到：

$$ \gamma = \frac{-0.2284}{-0.0662} \approx 3.45 $$

### 最终公式

将计算出的 $\gamma$ 代入，我们得到最终的经验值到等级的转换公式：

$$ L = \text{floor} \left( \min \left( 50, 1 + 49 \times \left( \frac{\ln(\text{exp} + 1)}{\ln(50001)} \right)^{3.45} \right) \right) $$

*注：程序中使用了 `floor` 向下取整，确保等级为整数。*

## 等级经验表示例

| 等级 | 升级所需经验 | 累计经验 |
| :--- | :------------- | :------- |
| 1    | 0              | 0        |
| 2    | 16             | 16       |
| 3    | 36             | 52       |
| 4    | 62             | 114      |
| 5    | 93             | 207      |
| ...  | ...            | ...      |
| 40   | 1131           | 24437    |
| 41   | 1230           | 25667    |
| ...  | ...            | ...      |
| 49   | 2470           | 47530    |
| 50   | 2471           | 50001    |

*这是一个简化的示例，详细的表格可以在 `output/reports/level_distribution.csv` 中找到。*