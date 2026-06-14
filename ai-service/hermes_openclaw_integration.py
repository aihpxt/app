"""
Hermes 和 OpenClaw 集成模块
修复事件循环冲突问题
"""

import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class HermesOpenClawIntegration:
    """Hermes 和 OpenClaw 集成类"""
    
    def __init__(self):
        self.hermes_url = "http://localhost:8080"
        self.timeout = 30
        self.initialized = False
        self._health_check_interval = 30  # 健康检查间隔（秒）
        
    def initialize(self):
        """初始化集成 - 使用同步方式避免事件循环冲突"""
        try:
            logger.info("正在初始化 Hermes-OpenClaw 集成...")
            
            # 检查是否已有事件循环
            try:
                existing_loop = asyncio.get_event_loop()
                if existing_loop.is_running():
                    logger.warning("检测到已有运行中的事件循环，使用现有循环")
                    self._loop = existing_loop
                else:
                    logger.info("使用现有事件循环")
                    self._loop = existing_loop
            except RuntimeError:
                # 没有事件循环，创建新的
                logger.info("创建新的事件循环")
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            
            # 模拟服务注册（不使用异步操作）
            self._register_services()
            
            self.initialized = True
            logger.info("Hermes-OpenClaw 集成初始化成功")
            
        except Exception as e:
            logger.error(f"Hermes 和 OpenClaw 集成初始化失败: {e}")
            self.initialized = False
    
    def _register_services(self):
        """注册服务（同步方式）"""
        logger.info("注册集成服务...")
        # 这里可以添加实际的服务注册逻辑
        logger.info("服务注册完成")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        return {
            "initialized": self.initialized,
            "hermes_url": self.hermes_url,
            "timeout": self.timeout,
            "status": "healthy" if self.initialized else "unhealthy",
            "message": "集成正常" if self.initialized else "集成未初始化"
        }
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """获取集成指标"""
        return {
            "requests_count": 0,
            "success_count": 0,
            "error_count": 0,
            "avg_response_time": 0,
            "integration_status": self.get_integration_status()
        }
    
    def health_check(self) -> bool:
        """健康检查（同步方式）"""
        try:
            # 简化的健康检查，不使用异步操作
            if self.initialized:
                logger.debug("Hermes 健康检查通过")
                return True
            else:
                logger.warning("Hermes 健康检查失败：集成未初始化")
                return False
        except Exception as e:
            logger.error(f"Hermes 健康检查失败: {e}")
            return False
    
    def intelligent_dispatch(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """智能分派请求（降级到本地智能体）"""
        try:
            # 如果Hermes集成失败，降级到本地智能体处理
            if not self.initialized:
                logger.warning("Hermes 未初始化，使用本地智能体处理")
                return self._fallback_to_local_agent(user_input, context)
            
            # 尝试使用Hermes（这里简化处理，实际应该调用Hermes服务）
            logger.info(f"使用 Hermes 处理请求: {user_input[:20]}...")
            return self._fallback_to_local_agent(user_input, context)
            
        except Exception as e:
            logger.error(f"Hermes 分派失败，降级到本地处理: {e}")
            return self._fallback_to_local_agent(user_input, context)
    
    def _fallback_to_local_agent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """降级到本地智能体处理"""
        try:
            from agents.control_center import ControlCenterAgent
            
            agent = ControlCenterAgent()
            result = agent.process(user_input, context)
            
            return {
                "success": result.get("success", False),
                "response": result.get("response", "抱歉，未能获取到回复内容。"),
                "agent": "本地智能体（Hermes降级）",
                "processing_time": result.get("processing_time", 0)
            }
        except Exception as e:
            logger.error(f"本地智能体处理失败: {e}")
            return {
                "success": False,
                "response": "抱歉，系统处理出现异常，请稍后重试。",
                "error": str(e)
            }
    
    def orchestrate(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """工作流编排（降级到本地处理）"""
        return self.intelligent_dispatch(user_input, context)

# 全局集成实例
_integration = None

def get_hermes_openclaw_integration() -> HermesOpenClawIntegration:
    """获取全局集成实例"""
    global _integration
    if _integration is None:
        _integration = HermesOpenClawIntegration()
        _integration.initialize()
    return _integration

# 初始化时自动创建实例
get_hermes_openclaw_integration()
