#!/usr/bin/env python3
"""
多平台信息抓取管理器
支持微信、字节系、小红书、地图等多个平台
"""

import time
from datetime import datetime
from typing import Dict, Any, List
from openclaw.real_api_client import get_api_client

class MultiPlatformCrawlerManager:
    """多平台信息抓取管理器"""
    
    def __init__(self, use_real_api: bool = False):
        """初始化多平台爬虫管理器"""
        self.api_client = get_api_client(use_real_api)
        self.platforms = {
            "wechat": self._init_wechat_crawler(),
            "douyin": self._init_douyin_crawler(),
            "xiaohongshu": self._init_xiaohongshu_crawler(),
            "weibo": self._init_weibo_crawler(),
            "bilibili": self._init_bilibili_crawler(),
            "map": self._init_map_crawler()
        }
    
    def _init_wechat_crawler(self):
        """初始化微信爬虫"""
        try:
            from openclaw.wechat_crawler import WechatCrawlerManager
            return WechatCrawlerManager()
        except ImportError:
            print("微信爬虫模块未找到")
            return None
    
    def _init_douyin_crawler(self):
        """初始化抖音爬虫"""
        class DouyinCrawler:
            def __init__(self, api_client):
                self.api_client = api_client
            
            def search_articles(self, keyword: str, count: int = 10) -> List[Dict[str, Any]]:
                return self.api_client.search_douyin(keyword, count)
        return DouyinCrawler(self.api_client)
    
    def _init_xiaohongshu_crawler(self):
        """初始化小红书爬虫"""
        class XiaohongshuCrawler:
            def __init__(self, api_client):
                self.api_client = api_client
            
            def search_articles(self, keyword: str, count: int = 10) -> List[Dict[str, Any]]:
                return self.api_client.search_xiaohongshu(keyword, count)
        return XiaohongshuCrawler(self.api_client)
    
    def _init_weibo_crawler(self):
        """初始化微博爬虫"""
        class WeiboCrawler:
            def __init__(self, api_client):
                self.api_client = api_client
            
            def search_articles(self, keyword: str, count: int = 10) -> List[Dict[str, Any]]:
                return self.api_client.search_weibo(keyword, count)
        return WeiboCrawler(self.api_client)
    
    def _init_bilibili_crawler(self):
        """初始化B站爬虫"""
        class BilibiliCrawler:
            def __init__(self, api_client):
                self.api_client = api_client
            
            def search_articles(self, keyword: str, count: int = 10) -> List[Dict[str, Any]]:
                return self.api_client.search_bilibili(keyword, count)
        return BilibiliCrawler(self.api_client)
    
    def _init_map_crawler(self):
        """初始化地图爬虫"""
        class MapCrawler:
            def __init__(self, api_client):
                self.api_client = api_client
            
            def search_schools(self, keyword: str, city: str = "昆明") -> List[Dict[str, Any]]:
                return self.api_client.search_map(keyword, city)
        return MapCrawler(self.api_client)
    
    def search_school_comprehensive(self, school_name: str) -> Dict[str, Any]:
        """
        综合搜索学校信息
        
        Args:
            school_name: 学校名称
            
        Returns:
            综合搜索结果
        """
        results = {
            "school_name": school_name,
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        # 微信搜索
        if self.platforms["wechat"]:
            try:
                wechat_result = self.platforms["wechat"].search_school_comprehensive(school_name)
                results["platforms"]["wechat"] = wechat_result
            except Exception as e:
                print(f"微信搜索失败: {e}")
        
        # 抖音搜索
        if self.platforms["douyin"]:
            try:
                douyin_result = self.platforms["douyin"].search_articles(school_name, count=5)
                results["platforms"]["douyin"] = douyin_result
            except Exception as e:
                print(f"抖音搜索失败: {e}")
        
        # 小红书搜索
        if self.platforms["xiaohongshu"]:
            try:
                xiaohongshu_result = self.platforms["xiaohongshu"].search_articles(school_name, count=5)
                results["platforms"]["xiaohongshu"] = xiaohongshu_result
            except Exception as e:
                print(f"小红书搜索失败: {e}")
        
        # 微博搜索
        if self.platforms["weibo"]:
            try:
                weibo_result = self.platforms["weibo"].search_articles(school_name, count=5)
                results["platforms"]["weibo"] = weibo_result
            except Exception as e:
                print(f"微博搜索失败: {e}")
        
        # B站搜索
        if self.platforms["bilibili"]:
            try:
                bilibili_result = self.platforms["bilibili"].search_articles(school_name, count=5)
                results["platforms"]["bilibili"] = bilibili_result
            except Exception as e:
                print(f"B站搜索失败: {e}")
        
        # 地图搜索
        if self.platforms["map"]:
            try:
                map_result = self.platforms["map"].search_schools(school_name)
                results["platforms"]["map"] = map_result
            except Exception as e:
                print(f"地图搜索失败: {e}")
        
        # 处理微博数据
        if self.platforms["weibo"]:
            try:
                weibo_result = self.platforms["weibo"].search_articles(keyword, count=5)
                results["platforms"]["weibo"] = weibo_result
            except Exception as e:
                print(f"微博搜索失败: {e}")
        
        # 处理B站数据
        if self.platforms["bilibili"]:
            try:
                bilibili_result = self.platforms["bilibili"].search_articles(keyword, count=5)
                results["platforms"]["bilibili"] = bilibili_result
            except Exception as e:
                print(f"B站搜索失败: {e}")
        
        return results
    
    def search_education_info(self, keyword: str) -> Dict[str, Any]:
        """
        搜索教育相关信息
        
        Args:
            keyword: 搜索关键词（如"中考政策"、"升学规划"等）
            
        Returns:
            综合搜索结果
        """
        results = {
            "keyword": keyword,
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        # 微信搜索
        if self.platforms["wechat"]:
            try:
                wechat_result = self.platforms["wechat"].get_policy_updates()
                results["platforms"]["wechat"] = wechat_result
            except Exception as e:
                print(f"微信搜索失败: {e}")
        
        # 抖音搜索
        if self.platforms["douyin"]:
            try:
                douyin_result = self.platforms["douyin"].search_articles(keyword, count=5)
                results["platforms"]["douyin"] = douyin_result
            except Exception as e:
                print(f"抖音搜索失败: {e}")
        
        # 小红书搜索
        if self.platforms["xiaohongshu"]:
            try:
                xiaohongshu_result = self.platforms["xiaohongshu"].search_articles(keyword, count=5)
                results["platforms"]["xiaohongshu"] = xiaohongshu_result
            except Exception as e:
                print(f"小红书搜索失败: {e}")
        
        return results
    
    def get_all_platforms(self) -> List[str]:
        """
        获取所有支持的平台
        
        Returns:
            平台名称列表
        """
        return list(self.platforms.keys())

# 便捷函数
def crawl_multi_platform_info(keyword: str) -> Dict[str, Any]:
    """
    多平台信息抓取便捷函数
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        抓取结果
    """
    manager = MultiPlatformCrawlerManager()
    if "学校" in keyword or "中学" in keyword:
        return manager.search_school_comprehensive(keyword)
    else:
        return manager.search_education_info(keyword)

if __name__ == "__main__":
    # 测试多平台爬虫
    manager = MultiPlatformCrawlerManager()
    
    # 测试学校搜索
    print("=== 测试学校搜索 ===")
    result = manager.search_school_comprehensive("云南师范大学附属中学")
    print(f"学校: {result['school_name']}")
    print(f"平台数: {len(result['platforms'])}")
    for platform, data in result['platforms'].items():
        if platform == "wechat":
            print(f"{platform}: 文章 {len(data.get('articles', []))} 篇, 招生信息 {len(data.get('admission_info', []))} 篇")
        else:
            print(f"{platform}: {len(data)} 条信息")
    
    # 测试教育信息搜索
    print("\n=== 测试教育信息搜索 ===")
    result = manager.search_education_info("中考政策")
    print(f"关键词: {result['keyword']}")
    print(f"平台数: {len(result['platforms'])}")
    for platform, data in result['platforms'].items():
        if platform == "wechat":
            print(f"{platform}: 政策 {len(data.get('policies', []))} 条, 热门话题 {len(data.get('hot_topics', []))} 条")
        else:
            print(f"{platform}: {len(data)} 条信息")