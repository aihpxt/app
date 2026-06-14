"""自动化日志分析系统"""

import re
import time
import json
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LogPattern:
    """日志模式定义"""
    
    def __init__(self, name: str, pattern: str, level: str = 'ERROR', severity: int = 1):
        self.name = name
        self.pattern = re.compile(pattern)
        self.level = level
        self.severity = severity  # 1-5，越高越严重
    
    def match(self, log_line: str) -> bool:
        """检查日志行是否匹配模式"""
        return self.pattern.search(log_line) is not None


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self):
        # 预定义的日志模式
        self._patterns = [
            LogPattern('connection_error', r'Connection.*error|ConnectionRefusedError|ConnectionResetError', 'ERROR', 4),
            LogPattern('timeout', r'timeout|TimeoutError', 'ERROR', 3),
            LogPattern('redis_error', r'Redis.*error|redis.*failed', 'ERROR', 4),
            LogPattern('database_error', r'Database.*error|SQL.*error|db.*failed', 'ERROR', 4),
            LogPattern('http_error', r'HTTP.*500|Internal Server Error', 'ERROR', 3),
            LogPattern('memory_warning', r'memory.*high|MemoryError', 'WARNING', 2),
            LogPattern('cpu_warning', r'CPU.*high|cpu.*overload', 'WARNING', 2),
            LogPattern('disk_warning', r'disk.*full|disk.*high', 'WARNING', 3),
            LogPattern('retry_failed', r'retry.*failed|max retries', 'ERROR', 3),
            LogPattern('rate_limit', r'rate limit|Too Many Requests', 'WARNING', 2),
            LogPattern('authentication_failed', r'auth.*failed|login.*failed|token.*invalid', 'WARNING', 3),
            LogPattern('invalid_input', r'invalid.*input|bad request|validation error', 'WARNING', 2),
            LogPattern('service_unavailable', r'service.*unavailable|down', 'ERROR', 4),
            LogPattern('network_error', r'network.*error|DNS.*failed', 'ERROR', 3),
            LogPattern('cache_error', r'cache.*error|cache.*miss', 'WARNING', 2),
        ]
        
        # 分析结果缓存
        self._analysis_cache = {}
        # 错误计数器
        self._error_counts = defaultdict(int)
        # 警告计数器
        self._warning_counts = defaultdict(int)
        # 最近的错误记录
        self._recent_errors = []
        # 分析时间窗口（分钟）
        self._analysis_window = 60
        
        logger.info("日志分析器初始化完成")
    
    def analyze_log_line(self, log_line: str) -> Dict[str, Any]:
        """
        分析单行日志
        
        Args:
            log_line: 日志行
        
        Returns:
            分析结果
        """
        result = {
            'line': log_line,
            'level': 'INFO',
            'patterns': [],
            'severity': 0,
            'is_error': False,
            'is_warning': False
        }
        
        # 提取日志级别
        if 'ERROR' in log_line:
            result['level'] = 'ERROR'
            result['is_error'] = True
        elif 'WARNING' in log_line:
            result['level'] = 'WARNING'
            result['is_warning'] = True
        
        # 匹配预定义模式
        matched_patterns = []
        max_severity = 0
        for pattern in self._patterns:
            if pattern.match(log_line):
                matched_patterns.append(pattern.name)
                max_severity = max(max_severity, pattern.severity)
        
        result['patterns'] = matched_patterns
        result['severity'] = max_severity
        
        # 更新计数器
        if result['is_error']:
            for p in matched_patterns:
                self._error_counts[p] += 1
        elif result['is_warning']:
            for p in matched_patterns:
                self._warning_counts[p] += 1
        
        # 记录最近错误
        if result['is_error'] and max_severity >= 3:
            self._recent_errors.append({
                'timestamp': time.time(),
                'line': log_line,
                'patterns': matched_patterns,
                'severity': max_severity
            })
            # 保留最近50条错误
            if len(self._recent_errors) > 50:
                self._recent_errors.pop(0)
        
        return result
    
    def analyze_log_file(self, file_path: str, lines_limit: int = 1000) -> Dict[str, Any]:
        """
        分析日志文件
        
        Args:
            file_path: 日志文件路径
            lines_limit: 最大读取行数
        
        Returns:
            分析结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-lines_limit:]
            
            results = []
            error_count = 0
            warning_count = 0
            pattern_counts = defaultdict(int)
            
            for line in lines:
                analysis = self.analyze_log_line(line.strip())
                results.append(analysis)
                
                if analysis['is_error']:
                    error_count += 1
                elif analysis['is_warning']:
                    warning_count += 1
                
                for p in analysis['patterns']:
                    pattern_counts[p] += 1
            
            return {
                'success': True,
                'total_lines': len(lines),
                'error_count': error_count,
                'warning_count': warning_count,
                'pattern_counts': dict(pattern_counts),
                'analysis_coverage': min(len([r for r in results if r['patterns']]) / len(results) * 100, 100),
                'recent_errors': self._recent_errors[-10:]
            }
        
        except Exception as e:
            logger.error(f"日志文件分析失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        return {
            'error_counts': dict(self._error_counts),
            'warning_counts': dict(self._warning_counts),
            'recent_errors': self._recent_errors[-20:],
            'total_errors': sum(self._error_counts.values()),
            'total_warnings': sum(self._warning_counts.values())
        }
    
    def detect_problems(self) -> List[Dict[str, Any]]:
        """
        检测潜在问题
        
        Returns:
            问题列表（按严重程度排序）
        """
        problems = []
        
        # 检查错误频率
        total_errors = sum(self._error_counts.values())
        if total_errors > 100:
            problems.append({
                'type': 'high_error_rate',
                'severity': 4,
                'message': f"高错误率：最近检测到 {total_errors} 个错误",
                'suggestion': '检查系统日志，定位高频错误原因'
            })
        
        # 检查严重错误类型
        critical_patterns = ['connection_error', 'database_error', 'redis_error', 'service_unavailable']
        for pattern in critical_patterns:
            if self._error_counts.get(pattern, 0) > 10:
                problems.append({
                    'type': pattern,
                    'severity': 5,
                    'message': f"严重错误：{pattern.replace('_', ' ')} 发生 {self._error_counts[pattern]} 次",
                    'suggestion': self._get_suggestion(pattern)
                })
        
        # 检查警告频率
        total_warnings = sum(self._warning_counts.values())
        if total_warnings > 500:
            problems.append({
                'type': 'high_warning_rate',
                'severity': 2,
                'message': f"高警告率：最近检测到 {total_warnings} 个警告",
                'suggestion': '检查系统配置，优化潜在问题'
            })
        
        # 检查超时问题
        if self._error_counts.get('timeout', 0) > 20:
            problems.append({
                'type': 'timeout_issues',
                'severity': 3,
                'message': f"超时问题：检测到 {self._error_counts['timeout']} 次超时",
                'suggestion': '检查网络连接和服务响应时间'
            })
        
        # 按严重程度排序
        problems.sort(key=lambda x: -x['severity'])
        
        return problems
    
    def _get_suggestion(self, problem_type: str) -> str:
        """获取问题建议"""
        suggestions = {
            'connection_error': '检查网络连接和目标服务状态',
            'database_error': '检查数据库连接和查询性能',
            'redis_error': '检查Redis服务状态和连接配置',
            'service_unavailable': '检查相关服务是否正常运行',
            'timeout': '增加超时时间或优化服务响应',
            'memory_warning': '检查内存使用情况，考虑扩容或优化',
            'cpu_warning': '检查CPU占用高的进程，优化代码',
            'disk_warning': '清理磁盘空间或扩展存储',
            'authentication_failed': '检查认证配置和凭证有效性',
            'rate_limit': '考虑增加限流阈值或优化请求频率'
        }
        return suggestions.get(problem_type, '检查相关组件状态')
    
    def generate_health_report(self, log_file_path: str = None) -> str:
        """
        生成健康报告
        
        Args:
            log_file_path: 日志文件路径（可选）
        
        Returns:
            报告文本
        """
        if log_file_path:
            analysis = self.analyze_log_file(log_file_path)
        else:
            analysis = self.get_error_summary()
        
        report = f"""📊 系统健康报告
{'-' * 50}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 日志分析摘要
"""
        
        if 'total_errors' in analysis:
            report += f"""• 错误总数: {analysis['total_errors']}
• 警告总数: {analysis['total_warnings']}
"""
        if 'error_count' in analysis:
            report += f"""• 错误数量: {analysis['error_count']}
• 警告数量: {analysis['warning_count']}
• 分析覆盖率: {analysis.get('analysis_coverage', 0):.1f}%
"""
        
        # 错误类型分布
        error_counts = analysis.get('error_counts', {})
        if error_counts:
            report += """
🔍 错误类型分布
"""
            for error_type, count in sorted(error_counts.items(), key=lambda x: -x[1])[:5]:
                report += f"• {error_type.replace('_', ' ')}: {count}次\n"
        
        # 检测到的问题
        problems = self.detect_problems()
        if problems:
            report += """
⚠️ 检测到的问题
"""
            for problem in problems:
                severity_icon = '🚨' if problem['severity'] >= 4 else '⚠️' if problem['severity'] >= 3 else 'ℹ️'
                report += f"{severity_icon} [{problem['severity']}] {problem['message']}\n"
                report += f"   建议: {problem['suggestion']}\n"
        else:
            report += """
✅ 系统运行正常，未检测到严重问题
"""
        
        # 最近错误
        recent_errors = analysis.get('recent_errors', [])[:5]
        if recent_errors:
            report += """
📝 最近错误
"""
            for i, error in enumerate(recent_errors, 1):
                line = error.get('line', error.get('message', ''))[:80]
                report += f"{i}. {line}\n"
        
        report += f"""
{'-' * 50}
报告结束
"""
        
        return report
    
    def reset_counters(self):
        """重置计数器"""
        self._error_counts.clear()
        self._warning_counts.clear()
        self._recent_errors.clear()


# 全局日志分析器
log_analyzer = LogAnalyzer()


def get_log_analyzer() -> LogAnalyzer:
    """获取日志分析器实例"""
    return log_analyzer


if __name__ == '__main__':
    # 测试日志分析器
    print("=" * 70)
    print("自动化日志分析器测试")
    print("=" * 70)
    
    analyzer = LogAnalyzer()
    
    # 测试日志行分析
    test_logs = [
        '2024-01-15 10:00:00 - app - ERROR - Connection refused',
        '2024-01-15 10:00:01 - app - WARNING - Memory usage high',
        '2024-01-15 10:00:02 - app - INFO - Service started',
        '2024-01-15 10:00:03 - app - ERROR - Redis connection failed',
        '2024-01-15 10:00:04 - app - ERROR - Database timeout',
    ]
    
    print("\n测试日志分析:")
    for log in test_logs:
        result = analyzer.analyze_log_line(log)
        print(f"日志: {log[:50]}...")
        print(f"  级别: {result['level']}, 模式: {result['patterns']}, 严重度: {result['severity']}")
    
    # 测试问题检测
    print("\n测试问题检测:")
    problems = analyzer.detect_problems()
    for problem in problems:
        print(f"  [{problem['severity']}] {problem['message']}")
    
    # 测试健康报告生成
    print("\n测试健康报告:")
    report = analyzer.generate_health_report()
    print(report)
    
    print("✅ 测试完成！")
    print("=" * 70)