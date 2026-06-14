#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能服务集成中心
统一管理所有智能化和自动化模块的协调工作
"""

import time
import json
import logging
from typing import Dict, Any, Optional
from threading import Lock
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartIntegrationCenter:
    """智能服务集成中心"""
    
    def __init__(self):
        self.gateway = None
        self.scheduler = None
        self.context_manager = None
        self.hermes_service = None
        self.adaptive_learning = None
        self.smart_cache = None
        
        self.initialized = False
        self.lock = Lock()
        
        # 性能指标
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "context_hits": 0,
            "context_misses": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def initialize(self):
        """初始化所有智能服务"""
        with self.lock:
            if self.initialized:
                return
            
            logger.info("开始初始化智能服务集成中心...")
            
            # 延迟导入避免循环依赖
            try:
                from smart_gateway import get_gateway
                self.gateway = get_gateway()
                logger.info("智能服务网关已初始化")
            except Exception as e:
                logger.warning(f"智能服务网关初始化失败: {e}")
            
            try:
                from enhanced_task_scheduler import get_scheduler
                self.scheduler = get_scheduler(max_workers=4)
                self.scheduler.start()
                logger.info("增强版任务调度器已初始化并启动")
            except Exception as e:
                logger.warning(f"任务调度器初始化失败: {e}")
            
            try:
                from enhanced_context_manager import get_context_manager
                self.context_manager = get_context_manager()
                logger.info("增强版上下文管理器已初始化")
            except Exception as e:
                logger.warning(f"上下文管理器初始化失败: {e}")
            
            try:
                from hermes_server import HermesService
                self.hermes_service = HermesService()
                logger.info("Hermes智能服务已初始化")
            except Exception as e:
                logger.warning(f"Hermes服务初始化失败: {e}")
            
            try:
                from adaptive_learning_system import AdaptiveLearningSystem
                self.adaptive_learning = AdaptiveLearningSystem()
                logger.info("自适应学习系统已初始化")
            except Exception as e:
                logger.warning(f"自适应学习系统初始化失败: {e}")
            
            try:
                from smart_cache import SmartCache
                self.smart_cache = SmartCache(max_size=2000, default_ttl=7200)
                logger.info("智能缓存系统已初始化")
            except Exception as e:
                logger.warning(f"智能缓存系统初始化失败: {e}")
            
            # 注册定时任务
            self._register_scheduled_tasks()
            
            self.initialized = True
            logger.info("智能服务集成中心初始化完成")
    
    def _register_scheduled_tasks(self):
        """注册定时任务"""
        if not self.scheduler:
            return
        
        from enhanced_task_scheduler import ScheduledTask, TaskPriority
        
        # 缓存预热任务
        def cache_warmer_task():
            """缓存预热任务"""
            if self.smart_cache:
                logger.info("执行缓存预热...")
                # 预热热点数据
                hot_topics = ["昆明重点高中", "师大附中", "昆一中", "中考政策", "分数推荐"]
                for topic in hot_topics:
                    self.smart_cache.set(topic, {"topic": topic, "cached": True})
                logger.info("缓存预热完成")
        
        # 上下文清理任务
        def context_cleanup_task():
            """上下文清理任务"""
            if self.context_manager:
                logger.info("执行上下文清理...")
                status = self.context_manager.get_status()
                logger.info(f"上下文状态: {status}")
        
        # 反馈分析任务
        def feedback_analysis_task():
            """反馈分析任务"""
            if self.adaptive_learning:
                logger.info("执行反馈分析...")
                # 分析最近的反馈数据
                self.adaptive_learning.analyze_recent_feedback()
        
        # 注册任务
        cache_task = ScheduledTask(
            task_id="cache_warmer",
            func=cache_warmer_task,
            schedule_type="interval",
            interval=3600,  # 每小时执行
            priority=TaskPriority.LOW
        )
        self.scheduler.add_task(cache_task)
        
        cleanup_task = ScheduledTask(
            task_id="context_cleanup",
            func=context_cleanup_task,
            schedule_type="interval",
            interval=1800,  # 每30分钟执行
            priority=TaskPriority.BACKGROUND
        )
        self.scheduler.add_task(cleanup_task)
        
        feedback_task = ScheduledTask(
            task_id="feedback_analysis",
            func=feedback_analysis_task,
            schedule_type="interval",
            interval=7200,  # 每2小时执行
            priority=TaskPriority.MEDIUM
        )
        self.scheduler.add_task(feedback_task)
        
        logger.info("定时任务注册完成")
    
    def process_request(self, user_input: str, session_id: str = None, 
                       user_id: str = None) -> Dict[str, Any]:
        """处理用户请求，协调各智能模块"""
        start_time = time.time()
        
        try:
            # 1. 获取会话上下文
            context_data = {}
            if self.context_manager and session_id:
                context_data = self.context_manager.get_session_context(session_id) or {}
                self.metrics["context_hits"] += 1
            else:
                self.metrics["context_misses"] += 1
            
            # 2. 使用Hermes进行意图分析和情感识别
            hermes_result = {}
            if self.hermes_service:
                try:
                    # 使用Hermes实际存在的方法
                    emotion = self.hermes_service.analyze_emotion(user_input)
                    intent = self.hermes_service.analyze_intent(user_input, context_data)
                    hermes_result = {
                        "emotion": emotion,
                        "intent": intent
                    }
                except Exception as e:
                    logger.warning(f"Hermes分析失败: {e}")
            
            # 3. 路由到合适的处理模块
            if self.gateway:
                result = self.gateway.route_request("ai", {
                    "message": user_input,
                    "session_id": session_id,
                    "context": context_data,
                    "hermes_insight": hermes_result
                })
            else:
                # 备用处理路径
                result = self._process_request_fallback(user_input, session_id, context_data)
            
            # 4. 更新上下文
            new_context = {}
            if self.context_manager and session_id and result.get("success"):
                new_context = result.get("context", {})
                if new_context:
                    self.context_manager.merge_session_context(session_id, new_context)
            
            # 5. 收集反馈（异步）
            if self.adaptive_learning and result.get("success"):
                self._collect_feedback_async(session_id, user_input, result)
            
            response_time = time.time() - start_time
            self.metrics["total_requests"] += 1
            self.metrics["successful_requests"] += 1
            self.metrics["avg_response_time"] = (
                (self.metrics["avg_response_time"] * (self.metrics["total_requests"] - 1) + response_time)
                / self.metrics["total_requests"]
            )
            
            return {
                "success": True,
                "response": result.get("response", "处理完成"),
                "context_updated": bool(new_context),
                "response_time": round(response_time, 3),
                "hermes_insight": hermes_result
            }
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics["total_requests"] += 1
            self.metrics["failed_requests"] += 1
            
            logger.error(f"请求处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_time": round(response_time, 3)
            }
    
    def _process_request_fallback(self, user_input: str, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """备用请求处理路径"""
        from agents.specialists import MasterSpecialist
        
        specialist = MasterSpecialist()
        response = specialist.handle(user_input, session_id=session_id, context=context)
        
        return {
            "success": True,
            "response": response,
            "context": {"last_input": user_input}
        }
    
    def _collect_feedback_async(self, session_id: str, user_input: str, result: Dict[str, Any]):
        """异步收集反馈"""
        import threading
        
        def collect():
            try:
                # 模拟反馈收集（实际应用中会有用户评分）
                feedback = {
                    "session_id": session_id,
                    "user_input": user_input,
                    "response": result.get("response", ""),
                    "timestamp": time.time()
                }
                self.adaptive_learning.record_observation(feedback)
            except Exception as e:
                logger.warning(f"反馈收集失败: {e}")
        
        threading.Thread(target=collect, daemon=True).start()
    
    def get_status(self) -> Dict[str, Any]:
        """获取集成中心状态"""
        status = {
            "initialized": self.initialized,
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "services": {
                "gateway": self.gateway is not None,
                "scheduler": self.scheduler is not None,
                "context_manager": self.context_manager is not None,
                "hermes_service": self.hermes_service is not None,
                "adaptive_learning": self.adaptive_learning is not None,
                "smart_cache": self.smart_cache is not None
            }
        }
        
        # 添加各服务状态
        if self.scheduler:
            status["scheduler_status"] = self.scheduler.get_status()
        
        if self.context_manager:
            status["context_status"] = self.context_manager.get_status()
        
        if self.gateway:
            status["gateway_status"] = self.gateway.get_status()
        
        return status
    
    def shutdown(self):
        """关闭集成中心"""
        logger.info("正在关闭智能服务集成中心...")
        
        if self.scheduler:
            self.scheduler.stop()
            logger.info("任务调度器已停止")
        
        self.initialized = False
        logger.info("智能服务集成中心已关闭")


# 全局集成中心实例
_integration_center = None

def get_integration_center() -> SmartIntegrationCenter:
    """获取全局集成中心实例"""
    global _integration_center
    if _integration_center is None:
        _integration_center = SmartIntegrationCenter()
    return _integration_center


if __name__ == "__main__":
    # 初始化集成中心
    center = get_integration_center()
    center.initialize()
    
    print("=== 智能服务集成中心测试 ===")
    print(f"初始化状态: {center.initialized}")
    
    # 获取状态
    status = center.get_status()
    print(f"\n系统状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # 测试请求处理
    print("\n=== 测试请求处理 ===")
    result = center.process_request("680分推荐学校", session_id="test-123")
    print(f"请求结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 再次获取状态
    status = center.get_status()
    print(f"\n处理后状态: {json.dumps(status['metrics'], indent=2)}")
    
    print("\n=== 测试完成 ===")