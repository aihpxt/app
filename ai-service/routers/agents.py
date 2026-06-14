"""
智能体API路由
提供总控中心智能体的API接口
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from agents import get_control_center, ControlCenterAgent

router = APIRouter(prefix="/api/agents", tags=["智能体"])


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    response: str
    session_id: Optional[str] = None
    intent: Optional[Dict[str, Any]] = None
    dispatch: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None


class AgentInfoResponse(BaseModel):
    """智能体信息响应"""
    name: str
    role: str
    welcome_message: str
    capabilities: list
    dispatch_rules: list
    stats: Dict[str, Any]


# 获取总控中心实例
def get_agent_instance() -> ControlCenterAgent:
    return get_control_center()


@router.get("/welcome")
async def get_welcome_message(agent: ControlCenterAgent = Depends(get_agent_instance)):
    """获取欢迎语"""
    return {
        "success": True,
        "welcome_message": agent.greet()
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent: ControlCenterAgent = Depends(get_agent_instance)
):
    """
    与总控中心智能体对话
    
    - **message**: 用户消息
    - **session_id**: 会话ID（可选）
    - **context**: 上下文信息（可选）
    """
    try:
        # 构建上下文，包含session_id
        context = request.context or {}
        if request.session_id:
            context["session_id"] = request.session_id
        
        result = agent.process(request.message, context)
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            session_id=result.get("session_id"),
            intent=result.get("intent"),
            dispatch=result.get("dispatch"),
            processing_time=result.get("processing_time")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.get("/info", response_model=AgentInfoResponse)
async def get_agent_info(agent: ControlCenterAgent = Depends(get_agent_instance)):
    """获取智能体信息"""
    info = agent.get_agent_info()
    return AgentInfoResponse(**info)


@router.get("/stats")
async def get_stats(agent: ControlCenterAgent = Depends(get_agent_instance)):
    """获取分派统计"""
    return {
        "success": True,
        "stats": agent.get_dispatch_stats()
    }


@router.post("/stats/reset")
async def reset_stats(agent: ControlCenterAgent = Depends(get_agent_instance)):
    """重置统计信息"""
    agent.reset_stats()
    return {
        "success": True,
        "message": "统计信息已重置"
    }


@router.get("/rules")
async def get_dispatch_rules(agent: ControlCenterAgent = Depends(get_agent_instance)):
    """获取分派规则"""
    return {
        "success": True,
        "rules": agent.dispatcher.get_dispatch_rules()
    }


@router.get("/list")
async def list_agents():
    """列出所有智能体"""
    from agents.specialists import list_all_agents
    return {
        "success": True,
        "total": 11,
        "agents": list_all_agents()
    }


@router.get("/agent/{agent_id}")
async def get_agent_by_id(agent_id: str):
    """根据ID获取智能体信息"""
    from agents.specialists import get_agent_by_id, AGENT_ID_MAP
    
    agent = get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")
    
    intent = None
    for i, aid in AGENT_ID_MAP.items():
        if aid == agent_id:
            intent = i
            break
    
    return {
        "success": True,
        "agent": {
            "id": agent_id,
            "intent": intent,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description
        }
    }


@router.post("/test")
async def test_dispatch(
    request: ChatRequest,
    agent: ControlCenterAgent = Depends(get_agent_instance)
):
    """
    测试意图识别和分派（不实际处理）
    
    - **message**: 测试消息
    """
    try:
        # 只进行意图识别，不分派
        intent_result = agent.dispatcher.recognize_intent(request.message)
        
        return {
            "success": True,
            "message": request.message,
            "intent": intent_result,
            "suggested_agent": intent_result.get("agent_name", "总控中心"),
            "confidence": intent_result.get("confidence", 0)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")