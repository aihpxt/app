#!/usr/bin/env python3
"""
日志分析脚本
用于定期收集和分析日志文件
"""

import os
import sys
import time
import logging
import schedule
import re
from collections import Counter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'log_analyzer.log'),
    filemode='a'
)

# 日志配置
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
ANALYSIS_INTERVAL = 1  # 分析间隔，单位：小时

# 日志文件列表
LOG_FILES = [
    'app.log',
    'service.log',
    'monitor.log',
    'backup.log',
    'cache_warmer.log'
]

def analyze_logs():
    """分析日志"""
    try:
        logging.info("开始分析日志...")
        
        for log_file in LOG_FILES:
            log_path = os.path.join(LOG_DIR, log_file)
            if not os.path.exists(log_path):
                logging.warning(f"日志文件不存在: {log_path}")
                continue
            
            # 分析日志文件
            analyze_log_file(log_path)
        
        logging.info("日志分析完成")
    except Exception as e:
        logging.error(f"分析日志失败: {e}")

def analyze_log_file(log_path):
    """分析单个日志文件"""
    try:
        logging.info(f"分析日志文件: {log_path}")
        
        # 读取日志文件
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            logs = f.readlines()
        
        # 统计错误和警告
        error_count = 0
        warning_count = 0
        error_messages = []
        
        for line in logs:
            if 'ERROR' in line:
                error_count += 1
                # 提取错误信息
                error_match = re.search(r'ERROR - (.*)', line)
                if error_match:
                    error_messages.append(error_match.group(1))
            elif 'WARNING' in line or 'WARN' in line:
                warning_count += 1
        
        # 统计错误类型
        error_counter = Counter(error_messages)
        top_errors = error_counter.most_common(5)
        
        # 生成分析报告
        report = f"""
        日志文件: {log_path}
        日志条数: {len(logs)}
        错误条数: {error_count}
        警告条数: {warning_count}
        常见错误:
        """
        
        for error, count in top_errors:
            report += f"  - {error}: {count} 次\n"
        
        logging.info(report)
        
        # 如果错误数量过多，发送警报
        if error_count > 10:
            logging.warning(f"日志文件 {log_path} 中错误数量过多: {error_count}")
    except Exception as e:
        logging.error(f"分析日志文件 {log_path} 失败: {e}")

def main():
    """主函数"""
    logging.info("开始日志分析任务...")
    
    # 立即执行一次分析
    analyze_logs()
    
    # 定时执行分析
    schedule.every(ANALYSIS_INTERVAL).hours.do(analyze_logs)
    
    # 运行定时任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("日志分析任务已停止")
            break
        except Exception as e:
            logging.error(f"日志分析任务运行过程中发生错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
