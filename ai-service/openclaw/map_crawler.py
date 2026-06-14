"""地图爬虫 - 面向各类地图抓取全省各地州学校信息"""

import time
import random
import requests
from typing import Dict, Any, List, Optional
import json

class MapCrawler:
    """地图爬虫类，用于从各类地图服务获取学校信息"""
    
    def __init__(self):
        self.map_apis = {
            "baidu": "http://api.map.baidu.com/place/v2/search",
            "amap": "https://restapi.amap.com/v3/place/text",
            "tencent": "https://apis.map.qq.com/ws/place/v1/search"
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        self.crawled_data = []
        self.max_retries = 3
        self.prefectures = [
            "昆明市", "曲靖市", "玉溪市", "保山市", "昭通市",
            "丽江市", "普洱市", "临沧市", "楚雄州", "红河州",
            "文山州", "西双版纳州", "大理州", "德宏州", "怒江州", "迪庆州"
        ]
        # 模拟API密钥（实际使用时需要替换为真实密钥）
        self.api_keys = {
            "baidu": "your_baidu_api_key",
            "amap": "your_amap_api_key",
            "tencent": "your_tencent_api_key"
        }
    
    def crawl_baidu_map(self, prefecture: str) -> List[Dict[str, Any]]:
        """从百度地图获取学校信息"""
        results = []
        
        try:
            # 模拟百度地图API响应
            # 实际使用时，这里应该调用真实的API
            results = [
                {
                    "name": f"{prefecture}第一中学",
                    "address": f"{prefecture}中心区",
                    "location": {
                        "lat": 25.0389 + random.uniform(-0.1, 0.1),
                        "lng": 102.7155 + random.uniform(-0.1, 0.1)
                    },
                    "phone": "0871-12345678",
                    "rating": 4.5,
                    "image_url": f"https://example.com/{prefecture}_school.jpg",
                    "map_source": "baidu",
                    "prefecture": prefecture
                },
                {
                    "name": f"{prefecture}第二中学",
                    "address": f"{prefecture}东城区",
                    "location": {
                        "lat": 25.0389 + random.uniform(-0.1, 0.1),
                        "lng": 102.7155 + random.uniform(-0.1, 0.1)
                    },
                    "phone": "0871-87654321",
                    "rating": 4.3,
                    "image_url": f"https://example.com/{prefecture}_school2.jpg",
                    "map_source": "baidu",
                    "prefecture": prefecture
                }
            ]
            
        except Exception as e:
            print(f"爬取百度地图失败: {e}")
            # 即使发生异常，也返回模拟数据
            results = [
                {
                    "name": f"{prefecture}第一中学",
                    "address": f"{prefecture}中心区",
                    "location": {
                        "lat": 25.0389,
                        "lng": 102.7155
                    },
                    "phone": "0871-12345678",
                    "rating": 4.5,
                    "image_url": f"https://example.com/{prefecture}_school.jpg",
                    "map_source": "baidu",
                    "prefecture": prefecture
                }
            ]
        
        return results
    
    def crawl_amap(self, prefecture: str) -> List[Dict[str, Any]]:
        """从高德地图获取学校信息"""
        results = []
        
        try:
            # 模拟高德地图API响应
            results = [
                {
                    "name": f"{prefecture}第三中学",
                    "address": f"{prefecture}西城区",
                    "location": {
                        "lat": 25.0389 + random.uniform(-0.1, 0.1),
                        "lng": 102.7155 + random.uniform(-0.1, 0.1)
                    },
                    "phone": "0871-11223344",
                    "rating": 4.4,
                    "image_url": f"https://example.com/{prefecture}_school3.jpg",
                    "map_source": "amap",
                    "prefecture": prefecture
                },
                {
                    "name": f"{prefecture}第四中学",
                    "address": f"{prefecture}南城区",
                    "location": {
                        "lat": 25.0389 + random.uniform(-0.1, 0.1),
                        "lng": 102.7155 + random.uniform(-0.1, 0.1)
                    },
                    "phone": "0871-44332211",
                    "rating": 4.2,
                    "image_url": f"https://example.com/{prefecture}_school4.jpg",
                    "map_source": "amap",
                    "prefecture": prefecture
                }
            ]
            
        except Exception as e:
            print(f"爬取高德地图失败: {e}")
            # 即使发生异常，也返回模拟数据
            results = [
                {
                    "name": f"{prefecture}第三中学",
                    "address": f"{prefecture}西城区",
                    "location": {
                        "lat": 25.0389,
                        "lng": 102.7155
                    },
                    "phone": "0871-11223344",
                    "rating": 4.4,
                    "image_url": f"https://example.com/{prefecture}_school3.jpg",
                    "map_source": "amap",
                    "prefecture": prefecture
                }
            ]
        
        return results
    
    def crawl_tencent_map(self, prefecture: str) -> List[Dict[str, Any]]:
        """从腾讯地图获取学校信息"""
        results = []
        
        try:
            # 模拟腾讯地图API响应
            results = [
                {
                    "name": f"{prefecture}第五中学",
                    "address": f"{prefecture}北城区",
                    "location": {
                        "lat": 25.0389 + random.uniform(-0.1, 0.1),
                        "lng": 102.7155 + random.uniform(-0.1, 0.1)
                    },
                    "phone": "0871-55667788",
                    "rating": 4.3,
                    "image_url": f"https://example.com/{prefecture}_school5.jpg",
                    "map_source": "tencent",
                    "prefecture": prefecture
                },
                {
                    "name": f"{prefecture}第六中学",
                    "address": f"{prefecture}高新区",
                    "location": {
                        "lat": 25.0389 + random.uniform(-0.1, 0.1),
                        "lng": 102.7155 + random.uniform(-0.1, 0.1)
                    },
                    "phone": "0871-88776655",
                    "rating": 4.1,
                    "image_url": f"https://example.com/{prefecture}_school6.jpg",
                    "map_source": "tencent",
                    "prefecture": prefecture
                }
            ]
            
        except Exception as e:
            print(f"爬取腾讯地图失败: {e}")
            # 即使发生异常，也返回模拟数据
            results = [
                {
                    "name": f"{prefecture}第五中学",
                    "address": f"{prefecture}北城区",
                    "location": {
                        "lat": 25.0389,
                        "lng": 102.7155
                    },
                    "phone": "0871-55667788",
                    "rating": 4.3,
                    "image_url": f"https://example.com/{prefecture}_school5.jpg",
                    "map_source": "tencent",
                    "prefecture": prefecture
                }
            ]
        
        return results
    
    def crawl_all_maps(self, prefecture: str) -> List[Dict[str, Any]]:
        """爬取所有地图服务"""
        all_results = []
        
        print(f"开始从百度地图爬取{prefecture}学校信息...")
        baidu_results = self.crawl_baidu_map(prefecture)
        all_results.extend(baidu_results)
        
        print(f"开始从高德地图爬取{prefecture}学校信息...")
        amap_results = self.crawl_amap(prefecture)
        all_results.extend(amap_results)
        
        print(f"开始从腾讯地图爬取{prefecture}学校信息...")
        tencent_results = self.crawl_tencent_map(prefecture)
        all_results.extend(tencent_results)
        
        return all_results
    
    def crawl_all_prefectures(self) -> List[Dict[str, Any]]:
        """爬取所有地州的学校信息"""
        all_results = []
        
        for prefecture in self.prefectures:
            print(f"\n开始爬取{prefecture}的学校信息...")
            prefecture_results = self.crawl_all_maps(prefecture)
            all_results.extend(prefecture_results)
            # 避免请求过于频繁
            time.sleep(1)
        
        self.crawled_data = all_results
        print(f"\n爬取完成，共获取 {len(all_results)} 条学校信息")
        return all_results
    
    def clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清洗数据"""
        cleaned_data = []
        seen_names = set()
        
        for item in data:
            # 去重
            if item['name'] not in seen_names:
                seen_names.add(item['name'])
                # 标准化数据格式
                cleaned_item = {
                    "id": f"map_{int(time.time())}_{random.randint(1000, 9999)}",
                    "name": item['name'].strip(),
                    "address": item['address'].strip(),
                    "location": item['location'],
                    "phone": item.get('phone', ''),
                    "rating": item.get('rating', 0),
                    "image_url": item.get('image_url', ''),
                    "map_source": item['map_source'],
                    "prefecture": item['prefecture'],
                    "crawled_at": time.strftime('%Y-%m-%d %H:%M:%S')
                }
                cleaned_data.append(cleaned_item)
        
        return cleaned_data
    
    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证数据"""
        valid_data = []
        
        for item in data:
            # 检查数据完整性
            if all(key in item for key in ['name', 'address', 'location', 'prefecture']):
                # 检查位置信息
                if 'lat' in item['location'] and 'lng' in item['location']:
                    valid_data.append(item)
        
        return valid_data
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = "map_school_data.json"):
        """保存数据到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}")
    
    def get_crawled_data(self) -> List[Dict[str, Any]]:
        """获取爬取的数据"""
        return self.crawled_data
    
    def get_crawl_stats(self) -> Dict[str, Any]:
        """获取爬取统计信息"""
        stats = {
            "total_items": len(self.crawled_data),
            "by_prefecture": {},
            "by_map_source": {},
            "last_crawled": time.strftime('%Y-%m-%d %H:%M:%S'),
            "version": "1.0.0"
        }
        
        for item in self.crawled_data:
            prefecture = item.get('prefecture', 'unknown')
            stats['by_prefecture'][prefecture] = stats['by_prefecture'].get(prefecture, 0) + 1
            
            map_source = item.get('map_source', 'unknown')
            stats['by_map_source'][map_source] = stats['by_map_source'].get(map_source, 0) + 1
        
        return stats

# 全局地图爬虫实例
map_crawler = MapCrawler()
