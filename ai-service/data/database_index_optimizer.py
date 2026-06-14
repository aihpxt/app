#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库索引优化脚本
用于分析和优化SQLite数据库的查询性能
"""

import sqlite3
import time
import logging
from pathlib import Path
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIndexOptimizer:
    """数据库索引优化器"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.optimization_report = {
            "database": db_path,
            "timestamp": datetime.now().isoformat(),
            "tables_analyzed": [],
            "indexes_created": [],
            "queries_analyzed": [],
            "performance_improvements": []
        }

    def connect(self):
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

    def get_all_tables(self):
        """获取所有表"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)
        return [row['name'] for row in self.cursor.fetchall()]

    def get_table_info(self, table_name):
        """获取表信息"""
        # 获取列信息
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [dict(row) for row in self.cursor.fetchall()]

        # 获取索引信息
        self.cursor.execute(f"PRAGMA index_list({table_name});")
        indexes = [dict(row) for row in self.cursor.fetchall()]

        # 获取表大小
        self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
        row_count = self.cursor.fetchone()['count']

        return {
            "columns": columns,
            "indexes": indexes,
            "row_count": row_count
        }

    def analyze_slow_queries(self, table_name):
        """分析慢查询"""
        slow_queries = []

        # 检查是否有全表扫描的查询
        # 通过EXPLAIN QUERY PLAN分析
        test_queries = [
            f"SELECT * FROM {table_name}",
            f"SELECT COUNT(*) FROM {table_name}",
            f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 10",
        ]

        for query in test_queries:
            try:
                start_time = time.time()
                self.cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                plan = self.cursor.fetchall()
                execution_time = time.time() - start_time

                query_info = {
                    "query": query,
                    "execution_time": execution_time,
                    "plan": [dict(row) for row in plan]
                }

                # 检查是否使用索引
                plan_text = " ".join([str(row) for row in plan])
                if "SCAN" in plan_text.upper() and "INDEX" not in plan_text.upper():
                    query_info["needs_optimization"] = True
                    query_info["reason"] = "全表扫描"
                else:
                    query_info["needs_optimization"] = False

                slow_queries.append(query_info)
            except Exception as e:
                logger.warning(f"分析查询失败: {query}, 错误: {e}")

        return slow_queries

    def create_recommended_indexes(self):
        """创建推荐的索引"""
        # 基于常见查询模式创建索引
        recommended_indexes = {
            "schools": [
                ("idx_schools_city", "city"),
                ("idx_schools_district", "district"),
                ("idx_schools_level", "level"),
                ("idx_schools_type", "school_type"),
                ("idx_schools_city_level", "city, level"),
                ("idx_schools_city_type", "city, school_type"),
                ("idx_schools_search", "name, city"),
            ],
            "policies": [
                ("idx_policies_city", "city"),
                ("idx_policies_year", "year"),
                ("idx_policies_type", "policy_type"),
                ("idx_policies_city_year", "city, year"),
            ],
            "users": [
                ("idx_users_username", "username"),
                ("idx_users_phone", "phone"),
                ("idx_users_status", "status"),
            ],
            "favorites": [
                ("idx_favorites_user", "user_id"),
                ("idx_favorites_school", "school_id"),
                ("idx_favorites_user_school", "user_id, school_id"),
            ],
            "chat_sessions": [
                ("idx_sessions_user", "user_id"),
                ("idx_sessions_created", "created_at"),
                ("idx_sessions_user_created", "user_id, created_at"),
            ],
            "chat_messages": [
                ("idx_messages_session", "session_id"),
                ("idx_messages_created", "created_at"),
            ],
            "usage_records": [
                ("idx_usage_user", "user_id"),
                ("idx_usage_created", "created_at"),
                ("idx_usage_user_created", "user_id, created_at"),
            ],
            "user_memberships": [
                ("idx_memberships_user", "user_id"),
                ("idx_memberships_status", "status"),
                ("idx_memberships_expire", "expire_time"),
                ("idx_memberships_user_status", "user_id, status"),
            ],
        }

        created_indexes = []

        for table_name, indexes in recommended_indexes.items():
            # 检查表是否存在
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?;
            """, (table_name,))

            if not self.cursor.fetchone():
                logger.info(f"表 {table_name} 不存在，跳过索引创建")
                continue

            for index_name, columns in indexes:
                try:
                    # 检查索引是否已存在
                    self.cursor.execute("""
                        SELECT name FROM sqlite_master
                        WHERE type='index' AND name=?;
                    """, (index_name,))

                    if self.cursor.fetchone():
                        logger.info(f"索引 {index_name} 已存在，跳过")
                        continue

                    # 创建索引
                    sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns});"
                    self.cursor.execute(sql)
                    self.conn.commit()

                    created_indexes.append({
                        "index_name": index_name,
                        "table": table_name,
                        "columns": columns,
                        "sql": sql
                    })
                    logger.info(f"成功创建索引: {index_name}")

                except Exception as e:
                    logger.error(f"创建索引失败 {index_name}: {e}")

        return created_indexes

    def analyze_database(self):
        """分析整个数据库"""
        logger.info("=" * 60)
        logger.info("开始数据库性能分析")
        logger.info("=" * 60)

        tables = self.get_all_tables()
        logger.info(f"发现 {len(tables)} 个表")

        total_tables = len(tables)
        for i, table_name in enumerate(tables, 1):
            logger.info(f"\n分析表 {i}/{total_tables}: {table_name}")

            table_info = self.get_table_info(table_name)
            logger.info(f"  行数: {table_info['row_count']}")
            logger.info(f"  列数: {len(table_info['columns'])}")
            logger.info(f"  现有索引数: {len(table_info['indexes'])}")

            # 分析慢查询
            slow_queries = self.analyze_slow_queries(table_name)
            needs_optimization = sum(1 for q in slow_queries if q.get("needs_optimization"))

            if needs_optimization > 0:
                logger.warning(f"  发现 {needs_optimization} 个需要优化的查询")

            self.optimization_report["tables_analyzed"].append({
                "table_name": table_name,
                "row_count": table_info['row_count'],
                "column_count": len(table_info['columns']),
                "existing_indexes": len(table_info['indexes']),
                "slow_queries": len(slow_queries),
                "needs_optimization": needs_optimization > 0
            })

        return self.optimization_report

    def optimize_database(self):
        """执行数据库优化"""
        logger.info("\n" + "=" * 60)
        logger.info("开始数据库优化")
        logger.info("=" * 60)

        # 创建推荐的索引
        logger.info("\n创建推荐索引...")
        created_indexes = self.create_recommended_indexes()
        logger.info(f"成功创建 {len(created_indexes)} 个索引")

        self.optimization_report["indexes_created"] = created_indexes

        # 运行ANALYZE优化查询计划
        logger.info("\n运行ANALYZE更新统计信息...")
        try:
            self.cursor.execute("ANALYZE;")
            self.conn.commit()
            logger.info("统计信息更新完成")
        except Exception as e:
            logger.error(f"ANALYZE失败: {e}")

        return self.optimization_report

    def test_optimization(self):
        """测试优化效果"""
        logger.info("\n" + "=" * 60)
        logger.info("测试优化效果")
        logger.info("=" * 60)

        test_queries = [
            ("SELECT * FROM schools WHERE city='昆明市' LIMIT 10;", "按城市查询学校"),
            ("SELECT * FROM policies WHERE year=2026 LIMIT 10;", "按年份查询政策"),
            ("SELECT COUNT(*) FROM users WHERE status='active';", "统计活跃用户"),
        ]

        results = []
        for query, description in test_queries:
            try:
                # 检查查询计划
                self.cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                plan = self.cursor.fetchall()

                # 执行查询并计时
                start_time = time.time()
                self.cursor.execute(query)
                self.cursor.fetchall()
                execution_time = time.time() - start_time

                plan_text = " ".join([str(row) for row in plan])

                result = {
                    "description": description,
                    "query": query,
                    "execution_time": execution_time,
                    "uses_index": "INDEX" in plan_text.upper(),
                    "is_scan": "SCAN" in plan_text.upper() and "INDEX" not in plan_text.upper()
                }

                results.append(result)
                logger.info(f"\n查询: {description}")
                logger.info(f"  执行时间: {execution_time:.4f}秒")
                logger.info(f"  使用索引: {result['uses_index']}")
                logger.info(f"  全表扫描: {result['is_scan']}")

            except Exception as e:
                logger.error(f"测试查询失败: {description}, 错误: {e}")

        return results

    def generate_report(self):
        """生成优化报告"""
        report_path = Path(self.db_path).parent / "optimization_report.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_report, f, ensure_ascii=False, indent=2)

        logger.info(f"\n优化报告已保存: {report_path}")

        # 生成文本报告
        text_report = []
        text_report.append("=" * 60)
        text_report.append("数据库索引优化报告")
        text_report.append("=" * 60)
        text_report.append(f"\n数据库: {self.optimization_report['database']}")
        text_report.append(f"时间: {self.optimization_report['timestamp']}")
        text_report.append(f"\n分析的表数: {len(self.optimization_report['tables_analyzed'])}")
        text_report.append(f"创建的索引数: {len(self.optimization_report['indexes_created'])}")

        text_report.append("\n\n表分析详情:")
        for table in self.optimization_report['tables_analyzed']:
            text_report.append(f"\n  {table['table_name']}:")
            text_report.append(f"    行数: {table['row_count']}")
            text_report.append(f"    需要优化: {'是' if table['needs_optimization'] else '否'}")

        text_report.append("\n\n创建的索引:")
        for index in self.optimization_report['indexes_created']:
            text_report.append(f"\n  {index['index_name']}:")
            text_report.append(f"    表: {index['table']}")
            text_report.append(f"    列: {index['columns']}")

        text_report_path = Path(self.db_path).parent / "optimization_report.txt"
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(text_report))

        logger.info(f"文本报告已保存: {text_report_path}")

        return self.optimization_report


def main():
    """主函数"""
    import sys

    # 获取数据库路径
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # 默认数据库路径
        base_dir = Path(__file__).parent
        db_path = base_dir / "school_platform.db"

    if not Path(db_path).exists():
        logger.error(f"数据库文件不存在: {db_path}")
        sys.exit(1)

    # 创建优化器
    optimizer = DatabaseIndexOptimizer(str(db_path))

    if not optimizer.connect():
        sys.exit(1)

    try:
        # 分析数据库
        optimizer.analyze_database()

        # 执行优化
        optimizer.optimize_database()

        # 测试优化效果
        optimizer.test_optimization()

        # 生成报告
        optimizer.generate_report()

        logger.info("\n" + "=" * 60)
        logger.info("数据库优化完成!")
        logger.info("=" * 60)

    finally:
        optimizer.close()


if __name__ == '__main__':
    main()
