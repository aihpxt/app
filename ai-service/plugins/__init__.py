"""
插件系统
"""

from .plugin_manager import PluginManager, plugin_manager
from .base import Plugin

__all__ = ["PluginManager", "plugin_manager", "Plugin"]