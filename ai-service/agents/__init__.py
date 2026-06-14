"""
智能体模块 - 云南省中考择校智能体系统
"""

from .control_center import ControlCenterAgent, get_control_center
from .intent_dispatcher import IntentDispatcher, get_dispatcher

# 延迟导入specialists模块，避免循环导入
__all__ = [
    'ControlCenterAgent',
    'get_control_center',
    'IntentDispatcher',
    'get_dispatcher'
]

# 动态导入函数
def get_specialist_agents():
    """动态导入专业智能体"""
    from .specialists import (
        BaseAgent,
        WebDeveloperAgent,
        UIDesignerAgent,
        InfoQueryAgent,
        MarketingAgent,
        OutProvinceAgent,
        FinanceAgent,
        LegalAgent,
        ConversionAgent,
        PaymentAgent,
        LogisticsAgent,
        get_agent,
        AGENTS
    )
    return {
        'BaseAgent': BaseAgent,
        'WebDeveloperAgent': WebDeveloperAgent,
        'UIDesignerAgent': UIDesignerAgent,
        'InfoQueryAgent': InfoQueryAgent,
        'MarketingAgent': MarketingAgent,
        'OutProvinceAgent': OutProvinceAgent,
        'FinanceAgent': FinanceAgent,
        'LegalAgent': LegalAgent,
        'ConversionAgent': ConversionAgent,
        'PaymentAgent': PaymentAgent,
        'LogisticsAgent': LogisticsAgent,
        'get_agent': get_agent,
        'AGENTS': AGENTS
    }

# 按需导入
def get_agent(*args, **kwargs):
    """获取智能体"""
    from .specialists import get_agent as _get_agent
    return _get_agent(*args, **kwargs)

def get_AGENTS():
    """获取智能体注册表"""
    from .specialists import AGENTS
    return AGENTS