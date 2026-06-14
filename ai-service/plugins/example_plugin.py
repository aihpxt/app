"""
示例插件
"""

from plugins.base import Plugin


class ExamplePlugin(Plugin):
    """
    示例插件
    """
    
    # 插件元数据
    name = "example"
    version = "1.0.0"
    description = "示例插件，演示插件系统的使用"
    author = "AI Assistant"
    url = "https://example.com"
    
    # 插件配置
    config = {
        "enabled": True,
        "api_key": "",
        "timeout": 30
    }
    
    def activate(self):
        """
        激活插件
        """
        print(f"激活插件: {self.name}")
        # 在这里可以进行插件初始化操作
    
    def deactivate(self):
        """
        停用插件
        """
        print(f"停用插件: {self.name}")
        # 在这里可以进行插件清理操作
    
    def on_chat(self, message, context):
        """
        处理聊天事件
        
        Args:
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        print(f"处理聊天消息: {message}")
        # 可以在这里添加自定义的聊天处理逻辑
        return None
    
    def on_analyze(self, text):
        """
        处理分析事件
        
        Args:
            text: 要分析的文本
            
        Returns:
            分析结果
        """
        print(f"分析文本: {text}")
        # 可以在这里添加自定义的文本分析逻辑
        return None