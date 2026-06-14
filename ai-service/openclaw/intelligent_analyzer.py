#!/usr/bin/env python3
"""
智能分析模块
对获取的数据进行智能分析，提供更有价值的洞察
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter, defaultdict
import re

def get_db_connection():
    """获取数据库连接"""
    db_path = "sqlite/data/unified_school_data.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

class IntelligentAnalyzer:
    """智能分析器"""
    
    def __init__(self):
        """初始化智能分析器"""
        self.conn = get_db_connection()
    
    def analyze_school_trends(self, school_name: str) -> Dict[str, Any]:
        """
        分析学校趋势
        
        Args:
            school_name: 学校名称
            
        Returns:
            趋势分析结果
        """
        cursor = self.conn.cursor()
        
        # 获取该学校的相关数据
        cursor.execute('''
        SELECT * FROM school_updates 
        WHERE school_name = ?
        ORDER BY publish_time DESC
        LIMIT 50
        ''', (school_name,))
        
        updates = cursor.fetchall()
        
        if not updates:
            return {"school_name": school_name, "message": "暂无数据"}
        
        # 分析更新类型分布
        update_types = [update['update_type'] for update in updates]
        type_distribution = Counter(update_types)
        
        # 分析时间趋势
        monthly_updates = defaultdict(int)
        for update in updates:
            if update['publish_time']:
                try:
                    date = datetime.fromisoformat(update['publish_time'])
                    month_key = f"{date.year}-{date.month:02d}"
                    monthly_updates[month_key] += 1
                except:
                    pass
        
        # 分析来源分布
        sources = [update['source'] for update in updates if update['source']]
        source_distribution = Counter(sources)
        
        return {
            "school_name": school_name,
            "total_updates": len(updates),
            "update_type_distribution": dict(type_distribution),
            "monthly_trend": dict(monthly_updates),
            "source_distribution": dict(source_distribution),
            "most_active_month": max(monthly_updates.items(), key=lambda x: x[1])[0] if monthly_updates else None,
            "insights": self._generate_school_insights(type_distribution, monthly_updates, source_distribution)
        }
    
    def _generate_school_insights(self, type_dist: Counter, monthly_trend: Dict, source_dist: Counter) -> List[str]:
        """生成学校洞察"""
        insights = []
        
        # 更新类型洞察
        if type_dist:
            most_common_type = type_dist.most_common(1)[0]
            insights.append(f"该学校最活跃的更新类型是'{most_common_type[0]}'，占比{most_common_type[1]/sum(type_dist.values())*100:.1f}%")
        
        # 时间趋势洞察
        if monthly_trend:
            recent_months = sorted(monthly_trend.items(), key=lambda x: x[0], reverse=True)[:3]
            avg_updates = sum(monthly_trend.values()) / len(monthly_trend)
            insights.append(f"近3个月平均每月更新{avg_updates:.1f}条信息")
            
            if recent_months[0][1] > avg_updates * 1.5:
                insights.append(f"最近更新频率显著增加，可能存在重要动态")
        
        # 来源分布洞察
        if source_dist:
            top_source = source_dist.most_common(1)[0]
            insights.append(f"主要信息来源是'{top_source[0]}'，占比{top_source[1]/sum(source_dist.values())*100:.1f}%")
        
        return insights
    
    def analyze_platform_comparison(self, keyword: str) -> Dict[str, Any]:
        """
        分析平台对比
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            平台对比分析结果
        """
        cursor = self.conn.cursor()
        
        # 获取各平台的相关数据
        cursor.execute('''
        SELECT source, COUNT(*) as count, AVG(like_count) as avg_likes
        FROM wechat_articles
        WHERE keyword LIKE ?
        GROUP BY source
        ''', (f'%{keyword}%',))
        
        platform_stats = cursor.fetchall()
        
        if not platform_stats:
            return {"keyword": keyword, "message": "暂无数据"}
        
        # 分析平台表现
        platform_comparison = []
        for stat in platform_stats:
            platform_comparison.append({
                "platform": stat['source'],
                "article_count": stat['count'],
                "avg_likes": stat['avg_likes'] or 0,
                "engagement_rate": (stat['avg_likes'] or 0) / stat['count'] * 100
            })
        
        # 找出最佳平台
        best_platform = max(platform_comparison, key=lambda x: x['engagement_rate'])
        
        return {
            "keyword": keyword,
            "platform_comparison": platform_comparison,
            "best_platform": best_platform['platform'],
            "insights": self._generate_platform_insights(platform_comparison, best_platform)
        }
    
    def _generate_platform_insights(self, platform_stats: List[Dict], best_platform: str) -> List[str]:
        """生成平台洞察"""
        insights = []
        
        # 最佳平台洞察
        insights.append(f"'{best_platform}'平台在该主题下表现最佳，用户参与度最高")
        
        # 平台对比洞察
        total_articles = sum(stat['article_count'] for stat in platform_stats)
        if total_articles > 0:
            for stat in platform_stats:
                percentage = stat['article_count'] / total_articles * 100
                if percentage > 50:
                    insights.append(f"'{stat['platform']}'平台占据了{percentage:.1f}%的内容份额")
        
        return insights
    
    def analyze_hot_topics(self, limit: int = 10) -> Dict[str, Any]:
        """
        分析热门话题
        
        Args:
            limit: 返回数量限制
            
        Returns:
            热门话题分析结果
        """
        cursor = self.conn.cursor()
        
        # 获取热门文章
        cursor.execute('''
        SELECT title, keyword, like_count, comment_count, source, publish_time
        FROM wechat_articles
        WHERE like_count > 0
        ORDER BY like_count DESC
        LIMIT ?
        ''', (limit,))
        
        articles = cursor.fetchall()
        
        if not articles:
            return {"message": "暂无热门数据"}
        
        # 分析热门关键词
        keywords = [article['keyword'] for article in articles if article['keyword']]
        keyword_distribution = Counter(keywords)
        
        # 分析热门来源
        sources = [article['source'] for article in articles if article['source']]
        source_distribution = Counter(sources)
        
        # 分析互动数据
        total_likes = sum(article['like_count'] for article in articles if article['like_count'])
        total_comments = sum(article['comment_count'] for article in articles if article['comment_count'])
        avg_engagement = (total_likes + total_comments) / len(articles)
        
        return {
            "hot_articles": [
                {
                    "title": article['title'],
                    "keyword": article['keyword'],
                    "likes": article['like_count'],
                    "comments": article['comment_count'],
                    "source": article['source'],
                    "publish_time": article['publish_time']
                }
                for article in articles
            ],
            "hot_keywords": dict(keyword_distribution.most_common(5)),
            "source_distribution": dict(source_distribution),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_engagement": avg_engagement,
            "insights": self._generate_hot_topic_insights(keyword_distribution, source_distribution, avg_engagement)
        }
    
    def _generate_hot_topic_insights(self, keyword_dist: Counter, source_dist: Counter, avg_engagement: float) -> List[str]:
        """生成热门话题洞察"""
        insights = []
        
        # 关键词洞察
        if keyword_dist:
            top_keyword = keyword_dist.most_common(1)[0]
            insights.append(f"最热门的话题是'{top_keyword[0]}'，出现{top_keyword[1]}次")
        
        # 来源洞察
        if source_dist:
            top_source = source_dist.most_common(1)[0]
            insights.append(f"热门内容主要来自'{top_source[0]}'平台")
        
        # 互动洞察
        insights.append(f"平均每条热门内容获得{avg_engagement:.0f}次互动")
        
        return insights
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        情感分析
        
        Args:
            text: 文本内容
            
        Returns:
            情感分析结果
        """
        # 简化情感分析（基于关键词）
        positive_keywords = ['优秀', '好', '推荐', '成功', '进步', '提升', '改善', '优势', '特色', '领先', '卓越']
        negative_keywords = ['差', '问题', '困难', '挑战', '下降', '不足', '缺点', '落后', '失败', '担忧']
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)
        
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return {"sentiment": "neutral", "score": 0, "confidence": 0}
        
        # 计算情感得分
        score = (positive_count - negative_count) / total_keywords
        confidence = min(total_keywords / 10, 1.0)  # 基于关键词数量的置信度
        
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": confidence,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count
        }
    
    def generate_comprehensive_report(self, school_name: str = None, keyword: str = None) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            school_name: 学校名称（可选）
            keyword: 搜索关键词（可选）
            
        Returns:
            综合分析报告
        """
        report = {
            "report_time": datetime.now().isoformat(),
            "sections": []
        }
        
        # 学校趋势分析
        if school_name:
            school_trends = self.analyze_school_trends(school_name)
            report["sections"].append({
                "type": "school_trends",
                "data": school_trends
            })
        
        # 平台对比分析
        if keyword:
            platform_comparison = self.analyze_platform_comparison(keyword)
            report["sections"].append({
                "type": "platform_comparison",
                "data": platform_comparison
            })
        
        # 热门话题分析
        hot_topics = self.analyze_hot_topics()
        report["sections"].append({
            "type": "hot_topics",
            "data": hot_topics
        })
        
        # 生成总结洞察
        report["summary"] = self._generate_report_summary(report["sections"])
        
        return report
    
    def _generate_report_summary(self, sections: List[Dict]) -> List[str]:
        """生成报告总结"""
        summary = []
        
        for section in sections:
            if section["type"] == "school_trends":
                data = section["data"]
                if "insights" in data:
                    summary.extend(data["insights"])
            
            elif section["type"] == "platform_comparison":
                data = section["data"]
                if "insights" in data:
                    summary.extend(data["insights"])
            
            elif section["type"] == "hot_topics":
                data = section["data"]
                if "insights" in data:
                    summary.extend(data["insights"])
        
        return summary
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

def analyze_school_data(school_name: str) -> Dict[str, Any]:
    """
    分析学校数据便捷函数
    
    Args:
        school_name: 学校名称
        
    Returns:
        分析结果
    """
    analyzer = IntelligentAnalyzer()
    try:
        result = analyzer.analyze_school_trends(school_name)
        return result
    finally:
        analyzer.close()

def analyze_platform_data(keyword: str) -> Dict[str, Any]:
    """
    分析平台数据便捷函数
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        分析结果
    """
    analyzer = IntelligentAnalyzer()
    try:
        result = analyzer.analyze_platform_comparison(keyword)
        return result
    finally:
        analyzer.close()

def generate_full_report(school_name: str = None, keyword: str = None) -> Dict[str, Any]:
    """
    生成完整报告便捷函数
    
    Args:
        school_name: 学校名称（可选）
        keyword: 搜索关键词（可选）
        
    Returns:
        完整分析报告
    """
    analyzer = IntelligentAnalyzer()
    try:
        result = analyzer.generate_comprehensive_report(school_name, keyword)
        return result
    finally:
        analyzer.close()

if __name__ == "__main__":
    # 测试智能分析功能
    analyzer = IntelligentAnalyzer()
    
    # 测试学校趋势分析
    print("=== 学校趋势分析 ===")
    result = analyzer.analyze_school_trends("云南师范大学附属中学")
    print(f"学校: {result['school_name']}")
    print(f"总更新数: {result['total_updates']}")
    print(f"洞察: {result['insights']}")
    
    # 测试平台对比分析
    print("\n=== 平台对比分析 ===")
    result = analyzer.analyze_platform_comparison("中考政策")
    print(f"关键词: {result['keyword']}")
    print(f"最佳平台: {result['best_platform']}")
    print(f"洞察: {result['insights']}")
    
    # 测试热门话题分析
    print("\n=== 热门话题分析 ===")
    result = analyzer.analyze_hot_topics()
    print(f"总点赞数: {result['total_likes']}")
    print(f"平均互动: {result['avg_engagement']:.0f}")
    print(f"洞察: {result['insights']}")
    
    # 测试情感分析
    print("\n=== 情感分析 ===")
    test_text = "该校教学质量优秀，师资力量雄厚，是学生理想的选择"
    result = analyzer.analyze_sentiment(test_text)
    print(f"情感: {result['sentiment']}")
    print(f"得分: {result['score']:.2f}")
    print(f"置信度: {result['confidence']:.2f}")
    
    analyzer.close()