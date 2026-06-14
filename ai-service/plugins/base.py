"""
插件基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Plugin(ABC):
    """
    插件基类
    """
    
    # 插件元数据
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    url: str = ""
    
    # 插件配置
    config: Dict[str, Any] = {}
    
    def __init__(self):
        """
        初始化插件
        """
        self.initialize()
    
    def initialize(self):
        """
        初始化插件（可重写）
        """
        pass
    
    @abstractmethod
    def activate(self):
        """
        激活插件
        """
        pass
    
    @abstractmethod
    def deactivate(self):
        """
        停用插件
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        Returns:
            插件信息字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "url": self.url,
            "config": self.config
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取插件配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """
        设置插件配置
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def on_event(self, event: str, *args, **kwargs) -> Optional[Any]:
        """
        处理事件
        
        Args:
            event: 事件名称
            *args: 事件参数
            **kwargs: 事件关键字参数
            
        Returns:
            事件处理结果
        """
        method_name = f"on_{event}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(*args, **kwargs)
        return None