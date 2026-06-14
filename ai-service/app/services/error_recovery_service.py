#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误恢复与容错服务
负责无法回答问题识别、自动重试、友好错误提示生成
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Callable
import traceback
import time
import random

logger = logging.getLogger(__name__)


class ErrorRecoveryService:
    """错误恢复与容错服务"""
    
    def __init__(self):
        # 无法回答的问题模式
        self.UNANSWERABLE_PATTERNS = [
            # 无关问题
            r'(你好|您好|哈喽|hi|hello)',
            r'(吃饭|睡觉|天气|时间|日期)',
            r'(聊天|闲聊|随便说|说点什么)',
            r'(谢谢|感谢|不客气)',
            r'(再见|拜拜|结束|退出)',
            
            # 超出领域的问题
            r'(数学题|物理题|化学题|英语)',
            r'(新闻|娱乐|体育|股票|财经)',
            r'(游戏|电影|音乐|明星)',
            
            # 无意义问题
            r'^[\s\u3000]+$',
            r'^[a-zA-Z]+$',
            r'^[0-9]+$',
            r'^[!@#$%^&*()]+$',
            
            # 反问/挑衅
            r'(你知道|你能|你会|你是谁)',
            r'(为什么|怎么不|凭什么)',
        ]
        
        # 友好错误提示模板
        self.ERROR_MESSAGES = {
            'unanswerable': [
                '抱歉，我不太理解你的问题。我主要专注于中考择校相关的咨询服务。',
                '不好意思，这个问题超出了我的知识范围。你可以问我关于学校、招生政策等方面的问题。',
                '抱歉，我暂时无法回答这个问题。请问有什么关于中考或学校的问题需要咨询吗？',
            ],
            'service_error': [
                '抱歉，服务暂时出现故障，请稍后再试。',
                '服务遇到了一些问题，正在努力恢复中，请耐心等待。',
                '系统暂时无法响应，请稍后重新提问。',
            ],
            'timeout': [
                '查询时间过长，请简化你的问题或稍后再试。',
                '服务器响应较慢，请稍等片刻再提问。',
                '请求超时，请重新尝试或换一种方式提问。',
            ],
            'validation_error': [
                '请提供有效的信息，例如：分数范围在300-700分之间。',
                '输入格式有误，请检查后重新输入。',
                '信息验证失败，请提供正确的参数。',
            ],
            'rate_limit': [
                '提问过于频繁，请稍后再试。',
                '系统检测到频繁请求，请休息一下再提问。',
                '请求次数过多，请稍等片刻。',
            ],
            'default': [
                '抱歉，出现了一些问题，请再试一次。',
                '系统遇到了一些困难，请稍后重试。',
                '出错了，请刷新后重试。',
            ]
        }
        
        # 重试配置
        self.RETRY_CONFIG = {
            'max_retries': 3,
            'base_delay': 1.0,
            'max_delay': 5.0,
            'backoff_factor': 2.0
        }
        
        logger.info("错误恢复与容错服务初始化完成")
    
    def is_unanswerable(self, message: str) -> bool:
        """
        判断问题是否无法回答
        
        Args:
            message: 用户消息
        
        Returns:
            是否无法回答
        """
        if not message or not message.strip():
            return True
        
        message_clean = message.strip().lower()
        
        for pattern in self.UNANSWERABLE_PATTERNS:
            import re
            if re.search(pattern, message_clean):
                logger.debug(f"检测到无法回答的问题: {message}, 匹配模式: {pattern}")
                return True
        
        return False
    
    def generate_friendly_error(self, error_type: str = 'default', 
                                original_error: Optional[Exception] = None) -> str:
        """
        生成友好的错误提示信息
        
        Args:
            error_type: 错误类型
            original_error: 原始异常
        
        Returns:
            友好的错误提示
        """
        messages = self.ERROR_MESSAGES.get(error_type, self.ERROR_MESSAGES['default'])
        message = random.choice(messages)
        
        # 记录错误日志
        if original_error:
            logger.error(f"错误类型: {error_type}, 原始错误: {str(original_error)}")
            logger.error(f"错误堆栈:\n{traceback.format_exc()}")
        
        return message
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
        """
        带退避策略的重试机制
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            (是否成功, 结果或错误信息)
        """
        delay = self.RETRY_CONFIG['base_delay']
        max_retries = self.RETRY_CONFIG['max_retries']
        
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                return (True, result)
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                
                if attempt < max_retries - 1:
                    # 计算退避延迟
                    wait_time = min(delay * (self.RETRY_CONFIG['backoff_factor'] ** attempt), 
                                   self.RETRY_CONFIG['max_delay'])
                    logger.info(f"等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    # 最后一次尝试失败
                    logger.error(f"已达到最大重试次数 {max_retries}，放弃重试")
                    return (False, str(e))
        
        return (False, "重试次数已用尽")
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        统一错误处理入口
        
        Args:
            error: 异常对象
            context: 上下文信息
        
        Returns:
            友好的错误提示信息
        """
        error_type = self._classify_error(error)
        return self.generate_friendly_error(error_type, error)
    
    def _classify_error(self, error: Exception) -> str:
        """
        分类错误类型
        
        Args:
            error: 异常对象
        
        Returns:
            错误类型字符串
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # 根据错误消息分类
        if any(keyword in error_str for keyword in ['timeout', '超时', 'timed out']):
            return 'timeout'
        
        if any(keyword in error_str for keyword in ['validation', '验证', '格式', '参数']):
            return 'validation_error'
        
        if any(keyword in error_str for keyword in ['rate', 'limit', '频繁', '次数']):
            return 'rate_limit'
        
        # 根据异常类型分类
        if error_type in ['TimeoutError', 'ConnectionTimeout', 'ReadTimeout']:
            return 'timeout'
        
        if error_type in ['ValidationError', 'ValueError']:
            return 'validation_error'
        
        # 默认分类为服务错误
        return 'service_error'
    
    def fallback_response(self, original_question: str) -> str:
        """
        生成降级响应
        
        Args:
            original_question: 原始问题
        
        Returns:
            降级响应消息
        """
        responses = [
            f"关于'{original_question}'的问题，我正在查询相关信息，请稍后。",
            f"这个问题需要进一步核实，我会尽快给你回复。",
            f"对于'{original_question}'这个问题，建议你咨询学校招生办获取更准确的信息。",
            f"你可以尝试访问教育局官网了解'{original_question}'的相关信息。",
        ]
        
        return random.choice(responses)
    
    def validate_input(self, message: str) -> Tuple[bool, str]:
        """
        验证输入有效性
        
        Args:
            message: 用户输入
        
        Returns:
            (是否有效, 错误消息)
        """
        if not message or not message.strip():
            return (False, "请输入有效的问题")
        
        # 检查长度
        if len(message) > 500:
            return (False, "问题过长，请简化后再提问")
        
        # 检查是否包含危险字符
        dangerous_patterns = [r'<script', r'javascript:', r'onclick', r'onload']
        for pattern in dangerous_patterns:
            if pattern in message.lower():
                return (False, "输入包含不安全内容")
        
        return (True, "")
    
    def graceful_degradation(self, exception: Exception, 
                            fallback_func: Optional[Callable] = None) -> Any:
        """
        优雅降级处理
        
        Args:
            exception: 异常对象
            fallback_func: 降级函数
        
        Returns:
            降级结果
        """
        logger.warning(f"触发优雅降级: {type(exception).__name__}: {exception}")
        
        if fallback_func:
            try:
                return fallback_func()
            except Exception as fallback_error:
                logger.error(f"降级函数也失败了: {fallback_error}")
        
        return None
    
    def get_help_message(self) -> str:
        """获取帮助信息"""
        help_text = """
我可以帮助你解决中考择校相关的问题，例如：

🏫 学校信息查询
- "昆一中怎么样？"
- "介绍一下师大附中"

📊 录取概率分析
- "我考了650分，能上昆三中吗？"
- "630分能进哪些学校？"

📋 招生政策咨询
- "中考录取分数线是多少？"
- "志愿怎么填报？"

💡 择校建议
- "帮我推荐几所适合的学校"
- "昆一中和师大附中哪个好？"

有什么问题想问我吗？
        """.strip()
        
        return help_text


# 全局实例
error_recovery_service = ErrorRecoveryService()


def get_error_recovery_service() -> ErrorRecoveryService:
    """获取错误恢复服务实例"""
    return error_recovery_service


if __name__ == '__main__':
    print("=" * 70)
    print("错误恢复与容错服务测试")
    print("=" * 70)
    
    service = ErrorRecoveryService()
    
    # 测试1: 无法回答问题识别
    print("\n1. 测试无法回答问题识别")
    print("-" * 50)
    test_cases = [
        ("你好", True),
        ("今天天气怎么样", True),
        ("昆一中怎么样", False),
        ("谢谢", True),
        ("吃饭了吗", True),
        ("中考总分多少", False),
        ("abc123", True),
        ("!!!", True),
    ]
    
    for question, expected in test_cases:
        result = service.is_unanswerable(question)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{question}' -> {result} (预期: {expected})")
    
    # 测试2: 生成友好错误提示
    print("\n2. 测试友好错误提示")
    print("-" * 50)
    error_types = ['unanswerable', 'service_error', 'timeout', 'validation_error', 'rate_limit']
    for error_type in error_types:
        message = service.generate_friendly_error(error_type)
        print(f"{error_type}: {message}")
    
    # 测试3: 输入验证
    print("\n3. 测试输入验证")
    print("-" * 50)
    inputs = [
        ("", False),
        ("   ", False),
        ("a" * 600, False),
        ("正常问题", True),
        ("<script>alert('xss')</script>", False),
    ]
    
    for input_text, expected_valid in inputs:
        valid, msg = service.validate_input(input_text)
        status = "✓" if valid == expected_valid else "✗"
        print(f"{status} 输入验证: '{input_text[:20]}...' -> {valid} (消息: {msg})")
    
    # 测试4: 重试机制
    print("\n4. 测试重试机制")
    print("-" * 50)
    
    def flaky_function(success_on_attempt: int):
        flaky_function.attempts = getattr(flaky_function, 'attempts', 0) + 1
        if flaky_function.attempts >= success_on_attempt:
            return "成功！"
        raise ValueError("模拟失败")
    
    flaky_function.attempts = 0
    success, result = service.retry_with_backoff(flaky_function, success_on_attempt=2)
    print(f"第2次成功的函数: {success}, 结果: {result}")
    
    flaky_function.attempts = 0
    success, result = service.retry_with_backoff(flaky_function, success_on_attempt=5)
    print(f"第5次成功的函数(超过重试次数): {success}, 结果: {result}")
    
    # 测试5: 降级响应
    print("\n5. 测试降级响应")
    print("-" * 50)
    for i in range(3):
        response = service.fallback_response("昆一中录取分数线")
        print(f"降级响应 {i+1}: {response}")
    
    # 测试6: 错误分类
    print("\n6. 测试错误分类")
    print("-" * 50)
    
    test_errors = [
        TimeoutError("请求超时"),
        ValueError("参数验证失败"),
        Exception("服务器内部错误"),
    ]
    
    for error in test_errors:
        error_type = service._classify_error(error)
        print(f"{type(error).__name__}: {error_type}")
    
    # 测试7: 获取帮助信息
    print("\n7. 测试帮助信息")
    print("-" * 50)
    help_msg = service.get_help_message()
    print(help_msg)
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)