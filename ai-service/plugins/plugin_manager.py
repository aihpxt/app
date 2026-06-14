"""
插件管理器
"""

import os
import importlib
import inspect
from typing import Dict, List, Optional
from .base import Plugin


class PluginManager:
    """
    插件管理器
    """
    
    def __init__(self):
        """
        初始化插件管理器
        """
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dirs: List[str] = []
    
    def add_plugin_dir(self, directory: str):
        """
        添加插件目录
        
        Args:
            directory: 插件目录路径
        """
        if directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)
    
    def discover_plugins(self) -> List[str]:
        """
        发现插件
        
        Returns:
            插件名称列表
        """
        plugins = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
                    plugins.append(item)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        加载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件实例，加载失败返回None
        """
        try:
            # 尝试从插件目录加载
            for plugin_dir in self.plugin_dirs:
                plugin_path = os.path.join(plugin_dir, plugin_name)
                if os.path.exists(plugin_path):
                    # 导入插件模块
                    module_path = f"plugins.{plugin_name}"
                    module = importlib.import_module(module_path)
                    
                    # 查找插件类
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin:
                            # 创建插件实例
                            plugin = obj()
                            self.plugins[plugin_name] = plugin
                            return plugin
        except Exception as e:
            print(f"加载插件 {plugin_name} 失败: {e}")
        
        return None
    
    def load_all_plugins(self):
        """
        加载所有插件
        """
        plugins = self.discover_plugins()
        for plugin_name in plugins:
            self.load_plugin(plugin_name)
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """
        激活插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            激活成功返回True，否则返回False
        """
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].activate()
                return True
            except Exception as e:
                print(f"激活插件 {plugin_name} 失败: {e}")
        return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """
        停用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            停用成功返回True，否则返回False
        """
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].deactivate()
                return True
            except Exception as e:
                print(f"停用插件 {plugin_name} 失败: {e}")
        return False
    
    def activate_all_plugins(self):
        """
        激活所有插件
        """
        for plugin_name in self.plugins:
            self.activate_plugin(plugin_name)
    
    def deactivate_all_plugins(self):
        """
        停用所有插件
        """
        for plugin_name in self.plugins:
            self.deactivate_plugin(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件实例，不存在返回None
        """
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """
        获取所有插件
        
        Returns:
            插件字典
        """
        return self.plugins
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        获取插件信息
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件信息字典，不存在返回None
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_info()
        return None
    
    def get_all_plugin_info(self) -> List[Dict]:
        """
        获取所有插件信息
        
        Returns:
            插件信息列表
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def dispatch_event(self, event: str, *args, **kwargs) -> List[Any]:
        """
        分发事件
        
        Args:
            event: 事件名称
            *args: 事件参数
            **kwargs: 事件关键字参数
            
        Returns:
            事件处理结果列表
        """
        results = []
        for plugin in self.plugins.values():
            result = plugin.on_event(event, *args, **kwargs)
            if result is not None:
                results.append(result)
        return results


# 创建插件管理器实例
plugin_manager = PluginManager()

# 添加默认插件目录
plugin_manager.add_plugin_dir(os.path.join(os.path.dirname(__file__), "plugins"))