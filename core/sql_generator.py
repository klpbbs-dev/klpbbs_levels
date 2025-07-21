import csv
from typing import List, Tuple
from .query import exp_to_level


def generate_user_migration_csv(user_data: List[Tuple[int, int]], output_path: str):
    """
    生成用户积分迁移CSV文件

    参数:
        user_data: [(uid, exp), ...] 用户ID和经验值的元组列表
        output_path: 输出CSV文件路径
    """
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["uid", "exp", "old_level", "new_level"])

        for uid, exp in user_data:
            new_level = exp_to_level(exp)
            # 假设旧等级为简单的exp/1000（示例）
            old_level = min(50, max(1, exp // 1000 + 1))
            writer.writerow([uid, exp, old_level, new_level])

    print(f"用户迁移数据已保存到: {output_path}")


def generate_mysql_migration_script(
    table_name: str = "users", output_path: str = None
) -> str:
    """
    生成MySQL迁移脚本

    参数:
        table_name: 用户表名
        output_path: 输出文件路径

    返回:
        SQL脚本内容
    """
    sql_script = f"""
-- 论坛等级系统迁移SQL脚本 (MySQL版本)
-- 根据新的等级计算公式更新用户等级

-- 创建等级计算函数
DELIMITER //
DROP FUNCTION IF EXISTS calculate_level//
CREATE FUNCTION calculate_level(exp INT) RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE level_result INT;
    DECLARE exp_cap INT DEFAULT 50000;
    DECLARE gamma DECIMAL(10,2) DEFAULT 3.45;
    DECLARE base_val DECIMAL(10,6);
    DECLARE scaled_val DECIMAL(10,6);

    -- 处理负数经验值
    IF exp < 0 THEN
        SET exp = 0;
    END IF;

    -- 处理0经验值
    IF exp = 0 THEN
        RETURN 1;
    END IF;

    -- 计算等级
    SET base_val = LN(exp + 1) / LN(exp_cap + 1);
    SET scaled_val = POWER(base_val, gamma);
    SET level_result = 1 + 49 * scaled_val;

    -- 确保等级在1-50范围内
    IF level_result > 50 THEN
        SET level_result = 50;
    END IF;

    RETURN FLOOR(level_result);
END//
DELIMITER ;

-- 备份原有等级数据
CREATE TABLE IF NOT EXISTS {table_name}_level_backup AS
SELECT uid, level as old_level, exp, NOW() as backup_time
FROM {table_name};

-- 更新用户等级
UPDATE {table_name} 
SET level = calculate_level(exp)
WHERE exp IS NOT NULL;

-- 验证更新结果
SELECT 
    COUNT(*) as total_users,
    MIN(level) as min_level,
    MAX(level) as max_level,
    ROUND(AVG(level), 2) as avg_level
FROM {table_name};

-- 等级分布统计
SELECT 
    level,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table_name}), 2) as percentage
FROM {table_name}
GROUP BY level
ORDER BY level;

-- 迁移前后对比
SELECT 
    b.old_level,
    u.level as new_level,
    COUNT(*) as user_count
FROM {table_name} u
JOIN {table_name}_level_backup b ON u.uid = b.uid
WHERE b.old_level != u.level
GROUP BY b.old_level, u.level
ORDER BY b.old_level, u.level;
"""

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sql_script)
        print(f"MySQL迁移脚本已保存到: {output_path}")

    return sql_script


def generate_postgresql_migration_script(
    table_name: str = "users", output_path: str = None
) -> str:
    """
    生成PostgreSQL迁移脚本

    参数:
        table_name: 用户表名
        output_path: 输出文件路径

    返回:
        SQL脚本内容
    """
    sql_script = f"""
-- 论坛等级系统迁移SQL脚本 (PostgreSQL版本)
-- 根据新的等级计算公式更新用户等级

-- 创建等级计算函数
CREATE OR REPLACE FUNCTION calculate_level(exp INTEGER) RETURNS INTEGER AS $$
DECLARE
    level_result INTEGER;
    exp_cap INTEGER := 50000;
    gamma DECIMAL(10,2) := 3.45;
    base_val DECIMAL(10,6);
    scaled_val DECIMAL(10,6);
BEGIN
    -- 处理负数经验值
    IF exp < 0 THEN
        exp := 0;
    END IF;
    
    -- 处理0经验值
    IF exp = 0 THEN
        RETURN 1;
    END IF;
    
    -- 计算等级
    base_val := LN(exp + 1) / LN(exp_cap + 1);
    scaled_val := POWER(base_val, gamma);
    level_result := 1 + 49 * scaled_val;
    
    -- 确保等级在1-50范围内
    IF level_result > 50 THEN
        level_result := 50;
    END IF;
    
    RETURN FLOOR(level_result);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 备份原有等级数据
CREATE TABLE IF NOT EXISTS {table_name}_level_backup AS
SELECT uid, level as old_level, exp, NOW() as backup_time
FROM {table_name};

-- 更新用户等级
UPDATE {table_name} 
SET level = calculate_level(exp)
WHERE exp IS NOT NULL;

-- 验证更新结果
SELECT 
    COUNT(*) as total_users,
    MIN(level) as min_level,
    MAX(level) as max_level,
    ROUND(AVG(level), 2) as avg_level
FROM {table_name};

-- 等级分布统计
SELECT 
    level,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table_name}), 2) as percentage
FROM {table_name}
GROUP BY level
ORDER BY level;
"""

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sql_script)
        print(f"PostgreSQL迁移脚本已保存到: {output_path}")

    return sql_script


def generate_sqlite_migration_script(
    table_name: str = "users", output_path: str = None
) -> str:
    """
    生成SQLite迁移脚本

    参数:
        table_name: 用户表名
        output_path: 输出文件路径

    返回:
        SQL脚本内容
    """
    sql_script = f"""
-- 论坛等级系统迁移SQL脚本 (SQLite版本)
-- 根据新的等级计算公式更新用户等级

-- SQLite不支持自定义函数，使用CASE WHEN实现分段计算
-- 备份原有等级数据
CREATE TABLE IF NOT EXISTS {table_name}_level_backup AS
SELECT uid, level as old_level, exp, datetime('now') as backup_time
FROM {table_name};

-- 更新用户等级（使用分段函数近似计算）
UPDATE {table_name} 
SET level = 
    CASE 
        WHEN exp <= 0 THEN 1
        WHEN exp <= 50 THEN 2
        WHEN exp <= 100 THEN 2
        WHEN exp <= 200 THEN 3
        WHEN exp <= 500 THEN 4
        WHEN exp <= 800 THEN 5
        WHEN exp <= 1000 THEN 6
        WHEN exp <= 1500 THEN 7
        WHEN exp <= 2000 THEN 8
        WHEN exp <= 2500 THEN 9
        WHEN exp <= 3000 THEN 10
        WHEN exp <= 4000 THEN 11
        WHEN exp <= 5000 THEN 12
        WHEN exp <= 6000 THEN 13
        WHEN exp <= 7000 THEN 14
        WHEN exp <= 8000 THEN 15
        WHEN exp <= 9000 THEN 16
        WHEN exp <= 10000 THEN 19
        WHEN exp <= 12000 THEN 21
        WHEN exp <= 15000 THEN 26
        WHEN exp <= 18000 THEN 29
        WHEN exp <= 20000 THEN 33
        WHEN exp <= 25000 THEN 40
        WHEN exp <= 30000 THEN 43
        WHEN exp <= 40000 THEN 47
        WHEN exp >= 50000 THEN 50
        ELSE CAST((1 + 49 * POWER(LOG(exp + 1) / LOG(50001), 3.45)) AS INTEGER)
    END
WHERE exp IS NOT NULL;

-- 验证更新结果
SELECT 
    COUNT(*) as total_users,
    MIN(level) as min_level,
    MAX(level) as max_level,
    ROUND(AVG(level), 2) as avg_level
FROM {table_name};

-- 等级分布统计
SELECT 
    level,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table_name}), 2) as percentage
FROM {table_name}
GROUP BY level
ORDER BY level;
"""

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sql_script)
        print(f"SQLite迁移脚本已保存到: {output_path}")

    return sql_script


def generate_all_sql_scripts(table_name: str = "users", output_dir: str = "."):
    """
    生成所有数据库类型的迁移脚本

    参数:
        table_name: 用户表名
        output_dir: 输出目录
    """
    import os

    # 创建sql子目录
    sql_dir = os.path.join(output_dir, "sql")
    os.makedirs(sql_dir, exist_ok=True)

    scripts = {
        "mysql": generate_mysql_migration_script,
        "postgresql": generate_postgresql_migration_script,
        "sqlite": generate_sqlite_migration_script,
    }

    for db_type, generator in scripts.items():
        output_path = os.path.join(sql_dir, f"migration_{db_type}.sql")
        generator(table_name, output_path)

    print(f"所有SQL迁移脚本已生成到: {sql_dir}")


if __name__ == "__main__":
    # 生成所有类型的SQL脚本
    generate_all_sql_scripts()
