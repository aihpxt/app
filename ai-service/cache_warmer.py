#!/usr/bin/env python3
"""
缓存预热脚本
用于定期预热和更新缓存
"""

import os
import sys
import time
import logging
import schedule
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'cache_warmer.log'),
    filemode='a'
)

# 服务配置
API_BASE_URL = "http://127.0.0.1:8000/api"
WARMUP_INTERVAL = 1  # 预热间隔，单位：小时

# 预热关键词列表
WARMUP_KEYWORDS = [
    "中考志愿怎么填报？",
    "昆明有哪些好高中？",
    "云南中考政策解读",
    "高中学校排名",
    "中考分数查询",
    "高中录取分数线",
    "高中学校学费",
    "高中学校地址"
]

def warmup_cache():
    """预热缓存"""
    try:
        logging.info("开始预热缓存...")
        
        # 预热缓存
        for keyword in WARMUP_KEYWORDS:
            try:
                # 调用聊天接口，预热缓存
                response = requests.post(
                    f"{API_BASE_URL}/v1/agents/chat",
                    json={"question": keyword},
                    timeout=30
                )
                if response.status_code == 200:
                    logging.info(f"预热关键词 '{keyword}' 成功")
                else:
                    logging.warning(f"预热关键词 '{keyword}' 失败，状态码: {response.status_code}")
            except Exception as e:
                logging.error(f"预热关键词 '{keyword}' 失败: {e}")
            
            # 避免请求过于频繁
            time.sleep(1)
        
        logging.info("缓存预热完成")
    except Exception as e:
        logging.error(f"预热缓存失败: {e}")

def main():
    """主函数"""
    logging.info("开始缓存预热任务...")
    
    # 立即执行一次预热
    warmup_cache()
    
    # 定时执行预热
    schedule.every(WARMUP_INTERVAL).hours.do(warmup_cache)
    
    # 运行定时任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("缓存预热任务已停止")
            break
        except Exception as e:
            logging.error(f"缓存预热任务运行过程中发生错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
