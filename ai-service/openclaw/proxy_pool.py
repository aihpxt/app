"""
代理IP池模块
"""

import requests
import time
import random
import threading
import logging
from typing import Dict, Any, List, Optional

# 配置日志
logger = logging.getLogger('ProxyPool')

class ProxyPool:
    """
    代理IP池
    """
    
    def __init__(self, proxy_sources: List[str] = None, validate_interval: int = 600):
        """
        初始化代理IP池
        
        Args:
            proxy_sources: 代理IP来源列表
            validate_interval: 验证间隔（秒）
        """
        self.proxy_sources = proxy_sources or [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
        ]
        self.validate_interval = validate_interval
        self.proxies = []
        self.valid_proxies = []
        self.lock = threading.Lock()
        self.last_validate_time = 0
        self._stats = {"success": 0, "fail": 0}
    
    def get_proxies_from_source(self, source: str) -> List[str]:
        """
        从代理IP来源获取代理
        
        Args:
            source: 代理IP来源URL
            
        Returns:
            代理IP列表
        """
        try:
            response = requests.get(source, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                # 过滤空行和无效格式
                proxies = [p.strip() for p in proxies if p.strip() and ':' in p]
                logger.info(f"从 {source} 获取 {len(proxies)} 个代理")
                return proxies
            else:
                logger.warning(f"从 {source} 获取代理失败: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"从 {source} 获取代理失败: {type(e).__name__} - {e}")
        except Exception as e:
            logger.error(f"从 {source} 获取代理时发生未知错误: {e}")
        return []
    
    def validate_proxy(self, proxy: str) -> bool:
        """
        验证代理IP是否有效
        
        Args:
            proxy: 代理IP，格式为 ip:port
            
        Returns:
            是否有效
        """
        try:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            # 使用多个测试站点提高可靠性
            test_urls = [
                "http://httpbin.org/ip",
                "https://api.ipify.org?format=json"
            ]
            for test_url in test_urls:
                try:
                    response = requests.get(test_url, proxies=proxies, timeout=5)
                    if response.status_code == 200:
                        self._stats["success"] += 1
                        return True
                except requests.exceptions.RequestException:
                    continue
            
            self._stats["fail"] += 1
            return False
        except Exception:
            self._stats["fail"] += 1
            return False
    
    def update_proxies(self):
        """
        更新代理IP池
        """
        with self.lock:
            # 获取所有代理IP
            all_proxies = []
            for source in self.proxy_sources:
                proxies = self.get_proxies_from_source(source)
                all_proxies.extend(proxies)
            
            # 去重
            self.proxies = list(set(all_proxies))
            
            # 验证代理IP
            self.valid_proxies = []
            for proxy in self.proxies:
                if self.validate_proxy(proxy):
                    self.valid_proxies.append(proxy)
            
            self.last_validate_time = time.time()
            logger.info(f"更新代理IP池，有效代理: {len(self.valid_proxies)}, 统计: {self._stats}")
    
    def get_proxy(self) -> Optional[str]:
        """
        获取一个有效的代理IP
        
        Returns:
            代理IP，格式为 ip:port
        """
        with self.lock:
            # 检查是否需要更新代理IP池
            if time.time() - self.last_validate_time > self.validate_interval:
                self.update_proxies()
            
            # 如果没有有效代理，返回None
            if not self.valid_proxies:
                return None
            
            # 随机选择一个代理IP
            return random.choice(self.valid_proxies)
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """
        获取代理IP字典，用于requests库
        
        Returns:
            代理IP字典
        """
        proxy = self.get_proxy()
        if proxy:
            return {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
        return None
    
    def remove_proxy(self, proxy: str):
        """
        移除无效的代理IP
        
        Args:
            proxy: 代理IP
        """
        with self.lock:
            if proxy in self.valid_proxies:
                self.valid_proxies.remove(proxy)
                logger.warning(f"移除无效代理: {proxy}")

class ProxyManager:
    """
    代理管理器
    """
    
    def __init__(self):
        """
        初始化代理管理器
        """
        self.proxy_pool = ProxyPool()
        # 初始更新代理IP池
        self.proxy_pool.update_proxies()
    
    def get_proxy(self) -> Optional[str]:
        """
        获取一个有效的代理IP
        
        Returns:
            代理IP
        """
        return self.proxy_pool.get_proxy()
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """
        获取代理IP字典
        
        Returns:
            代理IP字典
        """
        return self.proxy_pool.get_proxy_dict()
    
    def remove_proxy(self, proxy: str):
        """
        移除无效的代理IP
        
        Args:
            proxy: 代理IP
        """
        self.proxy_pool.remove_proxy(proxy)
    
    def update_proxies(self):
        """
        手动更新代理IP池
        """
        self.proxy_pool.update_proxies()

# 创建代理管理器实例
proxy_manager = ProxyManager()
