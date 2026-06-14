"""
行业信息自动更新模块
获取和分析教育行业趋势和统计信息
"""

import requests
import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class IndustryInfoUpdater:
    """行业信息更新器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.industry_sources = [
            {
                'name': '教育部',
                'url': 'http://www.moe.gov.cn',
                'category': '国家政策'
            },
            {
                'name': '中国教育报',
                'url': 'http://www.jyb.cn',
                'category': '行业新闻'
            },
            {
                'name': '中国教育在线',
                'url': 'http://www.eol.cn',
                'category': '行业资讯'
            },
            {
                'name': '云南省教育厅',
                'url': 'http://jyt.yn.gov.cn',
                'category': '地方动态'
            }
        ]
        
    def update_industry_info(self) -> Dict:
        """更新行业信息"""
        logger.info("开始更新行业信息...")
        
        results = {
            'trends': 0,
            'statistics': 0,
            'news': 0,
            'reports': 0,
            'total': 0,
            'details': []
        }
        
        # 1. 获取行业趋势
        trends = self._fetch_industry_trends()
        results['trends'] = len(trends)
        results['total'] += len(trends)
        
        for trend in trends:
            self._save_industry_trend(trend)
            results['details'].append({
                'type': 'trend',
                'title': trend.get('title', ''),
                'status': 'success'
            })
        
        # 2. 获取统计数据
        statistics = self._fetch_industry_statistics()
        results['statistics'] = len(statistics)
        results['total'] += len(statistics)
        
        for stat in statistics:
            self._save_industry_statistic(stat)
            results['details'].append({
                'type': 'statistic',
                'title': stat.get('title', ''),
                'status': 'success'
            })
        
        # 3. 获取行业新闻
        news = self._fetch_industry_news()
        results['news'] = len(news)
        results['total'] += len(news)
        
        for item in news:
            self._save_industry_news(item)
            results['details'].append({
                'type': 'news',
                'title': item.get('title', ''),
                'status': 'success'
            })
        
        # 4. 获取行业报告
        reports = self._fetch_industry_reports()
        results['reports'] = len(reports)
        results['total'] += len(reports)
        
        for report in reports:
            self._save_industry_report(report)
            results['details'].append({
                'type': 'report',
                'title': report.get('title', ''),
                'status': 'success'
            })
        
        logger.info(f"行业信息更新完成: 趋势 {results['trends']} 条, "
                   f"统计 {results['statistics']} 条, "
                   f"新闻 {results['news']} 条, "
                   f"报告 {results['reports']} 条")
        
        return results

    def _fetch_industry_trends(self) -> List[Dict]:
        """获取行业趋势"""
        trends = []
        
        try:
            # 从多个数据源获取趋势信息
            for source in self.industry_sources:
                try:
                    source_trends = self._fetch_trends_from_source(source)
                    trends.extend(source_trends)
                except Exception as e:
                    logger.warning(f"从 {source['name']} 获取趋势失败: {e}")
                    continue
            
            # 去重
            trends = self._deduplicate_trends(trends)
            
        except Exception as e:
            logger.error(f"获取行业趋势失败: {e}")
        
        return trends[:20]  # 限制返回数量

    def _fetch_trends_from_source(self, source: Dict) -> List[Dict]:
        """从指定数据源获取趋势"""
        trends = []
        
        try:
            response = requests.get(source['url'], timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return trends
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取趋势相关内容
            trend_keywords = ['趋势', '发展', '改革', '创新', '变化', '动向']
            
            # 查找包含趋势关键词的标题
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            
            for heading in headings:
                title = heading.get_text(strip=True)
                
                # 检查是否包含趋势关键词
                if any(keyword in title for keyword in trend_keywords):
                    # 提取链接
                    link = heading.find('a')
                    url = link.get('href', '') if link else ''
                    
                    if url:
                        # 构建完整URL
                        if url.startswith('/'):
                            url = source['url'] + url
                        elif not url.startswith('http'):
                            url = source['url'] + '/' + url
                        
                        trends.append({
                            'title': title,
                            'url': url,
                            'source': source['name'],
                            'category': source['category'],
                            'fetched_at': datetime.now().isoformat()
                        })
            
        except Exception as e:
            logger.error(f"从 {source['name']} 获取趋势失败: {e}")
        
        return trends[:10]  # 限制每个源返回数量

    def _deduplicate_trends(self, trends: List[Dict]) -> List[Dict]:
        """去重趋势"""
        seen = set()
        unique_trends = []
        
        for trend in trends:
            title = trend.get('title', '')
            # 使用标题的哈希值作为去重依据
            title_hash = hash(title)
            
            if title_hash not in seen:
                seen.add(title_hash)
                unique_trends.append(trend)
        
        return unique_trends

    def _fetch_industry_statistics(self) -> List[Dict]:
        """获取行业统计数据"""
        statistics = []
        
        try:
            # 从数据库获取学校统计信息
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 统计学校数量
            cursor.execute("SELECT COUNT(*) FROM schools")
            total_schools = cursor.fetchone()[0]
            
            # 按类型统计
            cursor.execute("SELECT type, COUNT(*) FROM schools GROUP BY type")
            type_stats = cursor.fetchall()
            
            # 按城市统计
            cursor.execute("SELECT city, COUNT(*) FROM schools GROUP BY city ORDER BY COUNT(*) DESC LIMIT 10")
            city_stats = cursor.fetchall()
            
            # 按分数线统计
            cursor.execute("SELECT AVG(minScore), MIN(minScore), MAX(minScore) FROM schools WHERE minScore > 0")
            score_stats = cursor.fetchone()
            
            conn.close()
            
            # 构建统计信息
            statistics.append({
                'title': '学校总数统计',
                'data': {
                    'total_schools': total_schools,
                    'type_distribution': {str(row[0]): row[1] for row in type_stats},
                    'top_cities': {row[0]: row[1] for row in city_stats}
                },
                'category': '学校统计',
                'updated_at': datetime.now().isoformat()
            })
            
            statistics.append({
                'title': '分数线统计',
                'data': {
                    'average_score': round(score_stats[0], 2) if score_stats[0] else 0,
                    'min_score': score_stats[1],
                    'max_score': score_stats[2]
                },
                'category': '分数线统计',
                'updated_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"获取行业统计失败: {e}")
        
        return statistics

    def _fetch_industry_news(self) -> List[Dict]:
        """获取行业新闻"""
        news = []
        
        try:
            # 从多个数据源获取新闻
            for source in self.industry_sources:
                try:
                    source_news = self._fetch_news_from_source(source)
                    news.extend(source_news)
                except Exception as e:
                    logger.warning(f"从 {source['name']} 获取新闻失败: {e}")
                    continue
            
            # 去重
            news = self._deduplicate_news(news)
            
        except Exception as e:
            logger.error(f"获取行业新闻失败: {e}")
        
        return news[:30]  # 限制返回数量

    def _fetch_news_from_source(self, source: Dict) -> List[Dict]:
        """从指定数据源获取新闻"""
        news_items = []
        
        try:
            response = requests.get(source['url'], timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return news_items
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻链接
            news_links = soup.find_all('a', href=re.compile(r'.*\.html?$'))
            
            for link in news_links[:15]:  # 限制获取数量
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                # 过滤掉非新闻链接
                if not self._is_news_link(href, title):
                    continue
                
                # 构建完整URL
                if href.startswith('/'):
                    url = source['url'] + href
                elif not href.startswith('http'):
                    url = source['url'] + '/' + href
                else:
                    url = href
                
                news_items.append({
                    'title': title,
                    'url': url,
                    'source': source['name'],
                    'category': source['category'],
                    'fetched_at': datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"从 {source['name']} 获取新闻失败: {e}")
        
        return news_items

    def _is_news_link(self, href: str, title: str) -> bool:
        """判断是否为新闻链接"""
        # 新闻关键词
        news_keywords = ['新闻', '资讯', '动态', '报道', '消息', '通知', '公告']
        
        # 检查标题是否包含新闻关键词
        for keyword in news_keywords:
            if keyword in title:
                return True
        
        return False

    def _deduplicate_news(self, news: List[Dict]) -> List[Dict]:
        """去重新闻"""
        seen = set()
        unique_news = []
        
        for item in news:
            title = item.get('title', '')
            # 使用标题的哈希值作为去重依据
            title_hash = hash(title)
            
            if title_hash not in seen:
                seen.add(title_hash)
                unique_news.append(item)
        
        return unique_news

    def _fetch_industry_reports(self) -> List[Dict]:
        """获取行业报告"""
        reports = []
        
        try:
            # 模拟获取行业报告
            reports = [
                {
                    'title': '2025年云南省教育发展报告',
                    'summary': '本报告分析了云南省教育发展的现状、趋势和挑战，提出了相应的政策建议。',
                    'category': '年度报告',
                    'fetched_at': datetime.now().isoformat()
                },
                {
                    'title': '民办教育发展现状与趋势分析',
                    'summary': '分析了民办教育的发展现状、面临的问题和未来发展趋势。',
                    'category': '专题报告',
                    'fetched_at': datetime.now().isoformat()
                },
                {
                    'title': '中考改革政策解读与影响分析',
                    'summary': '解读了最新的中考改革政策，分析了其对学校和学生的影响。',
                    'category': '政策解读',
                    'fetched_at': datetime.now().isoformat()
                }
            ]
            
        except Exception as e:
            logger.error(f"获取行业报告失败: {e}")
        
        return reports

    def _save_industry_trend(self, trend: Dict):
        """保存行业趋势"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查趋势是否已存在
            cursor.execute("SELECT id FROM industry_trends WHERE title = ?", (trend['title'],))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO industry_trends (title, url, source, category, fetched_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (trend['title'], trend['url'], trend['source'], 
                      trend['category'], trend['fetched_at']))
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"保存行业趋势失败: {e}")

    def _save_industry_statistic(self, statistic: Dict):
        """保存行业统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查统计是否已存在
            cursor.execute("SELECT id FROM industry_statistics WHERE title = ?", (statistic['title'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有统计
                cursor.execute('''
                    UPDATE industry_statistics 
                    SET data = ?, updated_at = ?
                    WHERE id = ?
                ''', (json.dumps(statistic['data'], ensure_ascii=False),
                      statistic['updated_at'], existing[0]))
            else:
                # 创建新统计
                cursor.execute('''
                    INSERT INTO industry_statistics (title, data, category, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (statistic['title'], json.dumps(statistic['data'], ensure_ascii=False),
                      statistic['category'], statistic['updated_at']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"保存行业统计失败: {e}")

    def _save_industry_news(self, news: Dict):
        """保存行业新闻"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查新闻是否已存在
            cursor.execute("SELECT id FROM industry_news WHERE title = ?", (news['title'],))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO industry_news (title, url, source, category, fetched_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (news['title'], news['url'], news['source'], 
                      news['category'], news['fetched_at']))
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"保存行业新闻失败: {e}")

    def _save_industry_report(self, report: Dict):
        """保存行业报告"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查报告是否已存在
            cursor.execute("SELECT id FROM industry_reports WHERE title = ?", (report['title'],))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO industry_reports (title, summary, category, fetched_at)
                    VALUES (?, ?, ?, ?)
                ''', (report['title'], report['summary'], 
                      report['category'], report['fetched_at']))
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"保存行业报告失败: {e}")