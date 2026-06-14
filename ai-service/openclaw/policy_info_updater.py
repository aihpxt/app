"""
政策信息自动更新模块
从官方网站获取和更新政策信息
"""

import requests
import json
import sqlite3
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class PolicyInfoUpdater:
    """政策信息更新器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.policy_sources = [
            {
                'name': '云南省教育厅',
                'url': 'http://jyt.yn.gov.cn',
                'policy_url': 'http://jyt.yn.gov.cn/zcwj/',
                'category': '省级政策'
            },
            {
                'name': '昆明市教育体育局',
                'url': 'http://jyj.km.gov.cn',
                'policy_url': 'http://jyj.km.gov.cn/zcwj/',
                'category': '市级政策'
            },
            {
                'name': '曲靖市教育体育局',
                'url': 'http://jyj.qj.gov.cn',
                'policy_url': 'http://jyj.qj.gov.cn/zcwj/',
                'category': '市级政策'
            },
            {
                'name': '玉溪市教育体育局',
                'url': 'http://jyj.yuxi.gov.cn',
                'policy_url': 'http://jyj.yuxi.gov.cn/zcwj/',
                'category': '市级政策'
            },
            {
                'name': '大理州教育体育局',
                'url': 'http://jyj.dali.gov.cn',
                'policy_url': 'http://jyj.dali.gov.cn/zcwj/',
                'category': '州级政策'
            }
        ]
        
    def update_policy_info(self) -> Dict:
        """更新政策信息"""
        logger.info("开始更新政策信息...")
        
        results = {
            'total': 0,
            'new': 0,
            'updated': 0,
            'failed': 0,
            'details': []
        }
        
        for source in self.policy_sources:
            try:
                logger.info(f"从 {source['name']} 获取政策信息...")
                policies = self._fetch_policies_from_source(source)
                
                for policy in policies:
                    try:
                        result = self._process_policy(policy, source)
                        results['total'] += 1
                        
                        if result['action'] == 'create':
                            results['new'] += 1
                        elif result['action'] == 'update':
                            results['updated'] += 1
                        
                        results['details'].append({
                            'title': policy['title'],
                            'source': source['name'],
                            'action': result['action'],
                            'status': 'success'
                        })
                        
                    except Exception as e:
                        results['failed'] += 1
                        logger.error(f"处理政策失败 {policy.get('title', 'unknown')}: {e}")
                        results['details'].append({
                            'title': policy.get('title', 'unknown'),
                            'source': source['name'],
                            'action': 'failed',
                            'status': 'error',
                            'error': str(e)
                        })
                
                logger.info(f"从 {source['name']} 完成: {len(policies)} 条政策")
                
            except Exception as e:
                logger.error(f"从 {source['name']} 获取政策失败: {e}")
                continue
        
        logger.info(f"政策更新完成: 新增 {results['new']} 条, 更新 {results['updated']} 条, 失败 {results['failed']} 条")
        return results

    def _fetch_policies_from_source(self, source: Dict) -> List[Dict]:
        """从指定数据源获取政策"""
        policies = []
        
        try:
            # 获取政策列表页面
            response = requests.get(source['policy_url'], timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logger.warning(f"获取 {source['name']} 政策列表失败: {response.status_code}")
                return policies
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取政策链接和标题
            policy_links = soup.find_all('a', href=re.compile(r'.*\.html?$'))
            
            for link in policy_links[:20]:  # 限制获取数量
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                # 过滤掉非政策链接
                if not self._is_policy_link(href, title):
                    continue
                
                # 构建完整URL
                if href.startswith('/'):
                    policy_url = source['url'] + href
                elif not href.startswith('http'):
                    policy_url = source['policy_url'] + href
                else:
                    policy_url = href
                
                # 获取政策详情
                policy_detail = self._fetch_policy_detail(policy_url, title, source)
                if policy_detail:
                    policies.append(policy_detail)
            
        except Exception as e:
            logger.error(f"从 {source['name']} 获取政策失败: {e}")
        
        return policies

    def _is_policy_link(self, href: str, title: str) -> bool:
        """判断是否为政策链接"""
        # 关键词过滤
        policy_keywords = ['政策', '通知', '办法', '规定', '意见', '方案', '公告', '文件']
        
        # 检查标题是否包含政策关键词
        for keyword in policy_keywords:
            if keyword in title:
                return True
        
        return False

    def _fetch_policy_detail(self, url: str, title: str, source: Dict) -> Optional[Dict]:
        """获取政策详情"""
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logger.warning(f"获取政策详情失败: {url}")
                return None
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取政策内容
            content_div = soup.find('div', class_='content') or soup.find('div', id='content') or soup.find('article')
            
            if content_div:
                content = content_div.get_text(strip=True)
            else:
                # 如果没有找到内容区域，提取整个body
                body = soup.find('body')
                if body:
                    content = body.get_text(strip=True)
                else:
                    content = response.text
            
            # 提取发布日期
            publish_date = self._extract_publish_date(soup, url)
            
            # 提取政策分类
            category = self._extract_policy_category(title, source['category'])
            
            return {
                'title': title,
                'content': content[:5000],  # 限制内容长度
                'category': category,
                'publish_date': publish_date,
                'source': source['name'],
                'url': url,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取政策详情失败 {url}: {e}")
            return None

    def _extract_publish_date(self, soup: BeautifulSoup, url: str) -> str:
        """提取发布日期"""
        # 尝试多种方式提取日期
        
        # 方法1: 查找日期元素
        date_patterns = [
            ('time', {'datetime': True}),
            ('span', {'class': re.compile(r'date|time')}),
            ('div', {'class': re.compile(r'date|time|publish')}),
            ('p', {'class': re.compile(r'date|time|publish')})
        ]
        
        for tag, attrs in date_patterns:
            element = soup.find(tag, attrs)
            if element:
                date_text = element.get_text(strip=True)
                date = self._parse_date(date_text)
                if date:
                    return date
        
        # 方法2: 从URL提取日期
        url_date = self._extract_date_from_url(url)
        if url_date:
            return url_date
        
        # 方法3: 使用当前日期
        return datetime.now().strftime('%Y-%m-%d')

    def _parse_date(self, date_text: str) -> Optional[str]:
        """解析日期文本"""
        # 常见日期格式
        date_patterns = [
            r'(\d{4})[-年/](\d{1,2})[-月/](\d{1,2})',
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                year, month, day = match.groups()
                try:
                    date = datetime(int(year), int(month), int(day))
                    return date.strftime('%Y-%m-%d')
                except:
                    continue
        
        return None

    def _extract_date_from_url(self, url: str) -> Optional[str]:
        """从URL提取日期"""
        # 查找URL中的日期模式
        date_pattern = r'/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/'
        match = re.search(date_pattern, url)
        
        if match:
            year, month, day = match.groups()
            try:
                date = datetime(int(year), int(month), int(day))
                return date.strftime('%Y-%m-%d')
            except:
                pass
        
        return None

    def _extract_policy_category(self, title: str, default_category: str) -> str:
        """提取政策分类"""
        # 政策分类关键词
        categories = {
            '招生政策': ['招生', '录取', '志愿', '报考'],
            '中考政策': ['中考', '初中', '学业水平'],
            '高考政策': ['高考', '大学', '招生'],
            '民办教育': ['民办', '私立', '非公办'],
            '义务教育': ['义务教育', '小学', '初中'],
            '高中教育': ['高中', '普高'],
            '职业教育': ['职业', '技校', '中专'],
            '教师政策': ['教师', '师资', '编制'],
            '收费政策': ['收费', '学费', '费用'],
            '安全管理': ['安全', '校园', '防护']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in title:
                    return category
        
        return default_category

    def _process_policy(self, policy: Dict, source: Dict) -> Dict:
        """处理政策"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查政策是否已存在
            cursor.execute("SELECT id, content FROM policies WHERE title = ?", (policy['title'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有政策
                policy_id = existing[0]
                old_content = existing[1]
                
                # 检查内容是否有变化
                if old_content != policy['content']:
                    cursor.execute('''
                        UPDATE policies 
                        SET content = ?, category = ?, publish_date = ?, source = ?
                        WHERE id = ?
                    ''', (policy['content'], policy['category'], 
                          policy['publish_date'], source['name'], policy_id))
                    
                    conn.commit()
                    logger.info(f"更新政策: {policy['title']}")
                    
                    return {
                        'action': 'update',
                        'policy_id': policy_id,
                        'changed': True
                    }
                else:
                    return {
                        'action': 'none',
                        'policy_id': policy_id,
                        'changed': False
                    }
            else:
                # 创建新政策
                cursor.execute('''
                    INSERT INTO policies (title, content, category, publish_date, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (policy['title'], policy['content'], 
                      policy['category'], policy['publish_date'], source['name']))
                
                policy_id = cursor.lastrowid
                conn.commit()
                logger.info(f"新增政策: {policy['title']}")
                
                return {
                    'action': 'create',
                    'policy_id': policy_id,
                    'changed': True
                }
                
        except Exception as e:
            conn.rollback()
            logger.error(f"处理政策失败: {e}")
            raise
        finally:
            conn.close()


class PolicyInfoValidator:
    """政策信息验证器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def validate_policy_info(self, policy_id: int) -> Dict:
        """验证政策信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
        policy = cursor.fetchone()
        
        if not policy:
            return {'valid': False, 'errors': ['政策不存在']}
        
        columns = [desc[0] for desc in cursor.description]
        policy_dict = dict(zip(columns, policy))
        
        errors = []
        warnings = []
        
        # 验证必填字段
        required_fields = ['title', 'content', 'category']
        for field in required_fields:
            if not policy_dict.get(field):
                errors.append(f"必填字段 {field} 为空")
        
        # 验证内容长度
        if policy_dict.get('content') and len(policy_dict['content']) < 50:
            warnings.append("政策内容过短")
        
        # 验证发布日期格式
        if policy_dict.get('publish_date'):
            if not self._validate_date(policy_dict['publish_date']):
                warnings.append("发布日期格式可能不正确")
        
        conn.close()
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_date(self, date_str: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False