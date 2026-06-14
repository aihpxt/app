"""智能体管理服务 - 整合11个智能体到小龙虾系统"""

import logging
from typing import Dict, Any, Optional, List
from .base_service import BaseService
# 延迟导入，避免循环导入
# from agents.specialists import AGENTS, AGENT_ID_MAP, get_agent, get_agent_by_id, list_all_agents
from agents.intent_dispatcher import get_dispatcher

logger = logging.getLogger(__name__)


class AgentManagementService(BaseService):
    """智能体管理服务"""
    
    def __init__(self):
        super().__init__("agent_management")
        self.dispatcher = get_dispatcher()
        self.agent_stats = {
            "total_requests": 0,
            "agent_distribution": {},
            "intent_distribution": {}
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有智能体"""
        # 动态导入，避免循环导入
        from agents.specialists import list_all_agents
        return list_all_agents()
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体信息"""
        # 动态导入，避免循环导入
        from agents.specialists import get_agent_by_id, AGENT_ID_MAP
        agent = get_agent_by_id(agent_id)
        if not agent:
            return None
        
        intent = None
        for i, aid in AGENT_ID_MAP.items():
            if aid == agent_id:
                intent = i
                break
        
        return {
            "id": agent_id,
            "intent": intent,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description
        }
    
    def dispatch_agent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """智能分派智能体处理消息"""
        # 识别意图
        intent_result = self.dispatcher.recognize_intent(message)
        intent = intent_result.get("intent", "control_center")
        
        # 分派给对应智能体
        dispatch_result = self.dispatcher.dispatch(intent_result, message, context)
        
        # 更新统计
        self.agent_stats["total_requests"] += 1
        self.agent_stats["intent_distribution"][intent] = \
            self.agent_stats["intent_distribution"].get(intent, 0) + 1
        
        agent_name = dispatch_result.get("agent", "总控智能体")
        self.agent_stats["agent_distribution"][agent_name] = \
            self.agent_stats["agent_distribution"].get(agent_name, 0) + 1
        
        return {
            "success": True,
            "intent": intent_result,
            "dispatch": dispatch_result,
            "response": dispatch_result.get("response"),
            "stats": self.agent_stats
        }
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """获取智能体统计信息"""
        return self.agent_stats
    
    def get_dispatch_rules(self) -> List[Dict[str, Any]]:
        """获取分派规则"""
        return self.dispatcher.get_dispatch_rules()
    
    def reset_stats(self) -> Dict[str, Any]:
        """重置统计信息"""
        self.agent_stats = {
            "total_requests": 0,
            "agent_distribution": {},
            "intent_distribution": {}
        }
        self.dispatcher.reset_stats()
        return {"success": True, "message": "统计信息已重置"}
    
    def process_weiyang_enrollment(self, user_input: str, student_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理未央中学招生相关咨询"""
        # 特殊处理未央中学相关问题
        context = {
            "student_info": student_info,
            "school": "丘北未央中学",
            "type": "enrollment"
        }
        
        result = self.dispatch_agent(user_input, context)
        
        # 增强未央中学相关回复
        response = result.get("response", "")
        if "未央" in user_input or "丘北" in user_input:
            # 添加未央中学特定信息
            enhanced_response = response + "\n\n【未央中学招生提醒】\n• 2026年招生已开始\n• 提供免费咨询和看校服务\n• 可预约一对一升学规划"
            result["response"] = enhanced_response
        
        return result
    
    def get_enrollment_status(self) -> Dict[str, Any]:
        """获取招生状态"""
        return {
            "school": "丘北未央中学",
            "status": "招生中",
            "enrollment_period": "2026年春季-秋季",
            "available_slots": {
                "junior": "剩余名额充足",
                "senior": "名额有限"
            },
            "services": [
                "免费咨询",
                "校园参观",
                "升学规划",
                "奖学金评估"
            ]
        }
