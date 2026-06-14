"""
数据验证和质量检查模块
检查和评估数据质量
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """数据质量检查器"""

    def __init__(self, db_path: str, update_history_db: str):
        self.db_path = db_path
        self.update_history_db = update_history_db
        
    def check_all_data(self) -> Dict:
        """检查所有数据质量"""
        logger.info("开始检查所有数据质量...")
        
        results = {
            'school': self._check_school_data_quality(),
            'policy': self._check_policy_data_quality(),
            'industry': self._check_industry_data_quality(),
            'overall': {}
        }
        
        # 计算总体质量评分
        results['overall'] = self._calculate_overall_quality(results)
        
        logger.info(f"数据质量检查完成: 总体评分 {results['overall']['score']:.2f}")
        return results

    def _check_school_data_quality(self) -> Dict:
        """检查学校数据质量"""
        logger.info("检查学校数据质量...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有学校
        cursor.execute("SELECT id, name, type, minScore, minRank, oneRate, address, phone, website, description FROM schools")
        schools = cursor.fetchall()
        
        quality_results = {
            'total': len(schools),
            'excellent': 0,
            'good': 0,
            'fair': 0,
            'poor': 0,
            'issues': [],
            'details': []
        }
        
        for school in schools:
            school_id = school[0]
            name = school[1]
            
            # 计算质量评分
            score = self._calculate_school_quality_score(school)
            
            # 分类
            if score >= 0.8:
                quality_results['excellent'] += 1
            elif score >= 0.6:
                quality_results['good'] += 1
            elif score >= 0.4:
                quality_results['fair'] += 1
            else:
                quality_results['poor'] += 1
            
            # 保存质量评分
            self._save_quality_score('school', school_id, score)
            
            # 检查问题
            issues = self._check_school_issues(school)
            if issues:
                quality_results['issues'].extend(issues)
                quality_results['details'].append({
                    'school_id': school_id,
                    'name': name,
                    'score': score,
                    'issues': issues
                })
        
        conn.close()
        
        logger.info(f"学校数据质量: 优秀 {quality_results['excellent']}, "
                   f"良好 {quality_results['good']}, "
                   f"一般 {quality_results['fair']}, "
                   f"较差 {quality_results['poor']}")
        
        return quality_results

    def _calculate_school_quality_score(self, school: Tuple) -> float:
        """计算学校数据质量评分"""
        school_id, name, school_type, min_score, min_rank, one_rate, address, phone, website, description = school
        
        scores = []
        
        # 1. 完整性评分
        completeness_score = 0.0
        if name: completeness_score += 0.2
        if school_type: completeness_score += 0.1
        if address: completeness_score += 0.2
        if phone: completeness_score += 0.2
        if website: completeness_score += 0.2
        if description: completeness_score += 0.1
        scores.append(completeness_score)
        
        # 2. 准确性评分
        accuracy_score = 0.0
        if min_score and min_score > 0 and min_score <= 750: accuracy_score += 0.3
        if min_rank and min_rank > 0: accuracy_score += 0.3
        if one_rate and 0 <= one_rate <= 1: accuracy_score += 0.4
        scores.append(accuracy_score)
        
        # 3. 格式正确性评分
        format_score = 0.0
        if phone and self._validate_phone(phone): format_score += 0.5
        if website and self._validate_website(website): format_score += 0.5
        scores.append(format_score)
        
        # 计算平均分
        return sum(scores) / len(scores) if scores else 0.0

    def _check_school_issues(self, school: Tuple) -> List[str]:
        """检查学校数据问题"""
        issues = []
        school_id, name, school_type, min_score, min_rank, one_rate, address, phone, website, description = school
        
        # 检查必填字段
        if not name:
            issues.append(f"学校ID {school_id}: 缺少学校名称")
        if not school_type:
            issues.append(f"学校 {name}: 缺少学校类型")
        
        # 检查数据范围
        if min_score is not None and min_score < 0:
            issues.append(f"学校 {name}: 最低分数为负数")
        if min_score is not None and min_score > 750:
            issues.append(f"学校 {name}: 最低分数超过750")
        if min_rank is not None and min_rank < 0:
            issues.append(f"学校 {name}: 最低排名为负数")
        if one_rate is not None and (one_rate < 0 or one_rate > 1):
            issues.append(f"学校 {name}: 一本率不在0-1范围内")
        
        # 检查数据格式
        if phone and not self._validate_phone(phone):
            issues.append(f"学校 {name}: 电话号码格式不正确")
        if website and not self._validate_website(website):
            issues.append(f"学校 {name}: 网站URL格式不正确")
        
        # 检查数据一致性
        if min_score is None and min_rank is not None:
            issues.append(f"学校 {name}: 有最低排名但没有最低分数")
        if min_score is not None and min_rank is None:
            issues.append(f"学校 {name}: 有最低分数但没有最低排名")
        
        return issues

    def _check_policy_data_quality(self) -> Dict:
        """检查政策数据质量"""
        logger.info("检查政策数据质量...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有政策
        cursor.execute("SELECT id, title, content, category, publish_date, source FROM policies")
        policies = cursor.fetchall()
        
        quality_results = {
            'total': len(policies),
            'excellent': 0,
            'good': 0,
            'fair': 0,
            'poor': 0,
            'issues': [],
            'details': []
        }
        
        for policy in policies:
            policy_id = policy[0]
            title = policy[1]
            
            # 计算质量评分
            score = self._calculate_policy_quality_score(policy)
            
            # 分类
            if score >= 0.8:
                quality_results['excellent'] += 1
            elif score >= 0.6:
                quality_results['good'] += 1
            elif score >= 0.4:
                quality_results['fair'] += 1
            else:
                quality_results['poor'] += 1
            
            # 保存质量评分
            self._save_quality_score('policy', policy_id, score)
            
            # 检查问题
            issues = self._check_policy_issues(policy)
            if issues:
                quality_results['issues'].extend(issues)
                quality_results['details'].append({
                    'policy_id': policy_id,
                    'title': title,
                    'score': score,
                    'issues': issues
                })
        
        conn.close()
        
        logger.info(f"政策数据质量: 优秀 {quality_results['excellent']}, "
                   f"良好 {quality_results['good']}, "
                   f"一般 {quality_results['fair']}, "
                   f"较差 {quality_results['poor']}")
        
        return quality_results

    def _calculate_policy_quality_score(self, policy: Tuple) -> float:
        """计算政策数据质量评分"""
        policy_id, title, content, category, publish_date, source = policy
        
        scores = []
        
        # 1. 完整性评分
        completeness_score = 0.0
        if title: completeness_score += 0.3
        if content: completeness_score += 0.4
        if category: completeness_score += 0.2
        if publish_date: completeness_score += 0.1
        scores.append(completeness_score)
        
        # 2. 内容质量评分
        content_score = 0.0
        if content and len(content) > 100: content_score += 0.5
        if content and len(content) > 500: content_score += 0.5
        scores.append(content_score)
        
        # 3. 时效性评分
        freshness_score = 0.0
        if publish_date:
            try:
                pub_date = datetime.strptime(publish_date, '%Y-%m-%d')
                days_old = (datetime.now() - pub_date).days
                
                if days_old < 30:
                    freshness_score = 1.0
                elif days_old < 90:
                    freshness_score = 0.8
                elif days_old < 180:
                    freshness_score = 0.6
                elif days_old < 365:
                    freshness_score = 0.4
                else:
                    freshness_score = 0.2
            except:
                pass
        scores.append(freshness_score)
        
        # 计算平均分
        return sum(scores) / len(scores) if scores else 0.0

    def _check_policy_issues(self, policy: Tuple) -> List[str]:
        """检查政策数据问题"""
        issues = []
        policy_id, title, content, category, publish_date, source = policy
        
        # 检查必填字段
        if not title:
            issues.append(f"政策ID {policy_id}: 缺少标题")
        if not content:
            issues.append(f"政策 {title}: 缺少内容")
        if not category:
            issues.append(f"政策 {title}: 缺少分类")
        
        # 检查内容长度
        if content and len(content) < 50:
            issues.append(f"政策 {title}: 内容过短")
        
        # 检查日期格式
        if publish_date and not self._validate_date(publish_date):
            issues.append(f"政策 {title}: 发布日期格式不正确")
        
        return issues

    def _check_industry_data_quality(self) -> Dict:
        """检查行业数据质量"""
        logger.info("检查行业数据质量...")
        
        quality_results = {
            'trends': self._check_industry_trends_quality(),
            'statistics': self._check_industry_statistics_quality(),
            'news': self._check_industry_news_quality(),
            'reports': self._check_industry_reports_quality()
        }
        
        return quality_results

    def _check_industry_trends_quality(self) -> Dict:
        """检查行业趋势质量"""
        # 这里实现行业趋势质量检查逻辑
        return {'total': 0, 'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}

    def _check_industry_statistics_quality(self) -> Dict:
        """检查行业统计质量"""
        # 这里实现行业统计质量检查逻辑
        return {'total': 0, 'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}

    def _check_industry_news_quality(self) -> Dict:
        """检查行业新闻质量"""
        # 这里实现行业新闻质量检查逻辑
        return {'total': 0, 'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}

    def _check_industry_reports_quality(self) -> Dict:
        """检查行业报告质量"""
        # 这里实现行业报告质量检查逻辑
        return {'total': 0, 'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}

    def _calculate_overall_quality(self, results: Dict) -> Dict:
        """计算总体质量评分"""
        school_score = self._calculate_category_score(results['school'])
        policy_score = self._calculate_category_score(results['policy'])
        industry_score = self._calculate_category_score(results['industry'])
        
        # 加权平均
        overall_score = (school_score * 0.5 + policy_score * 0.3 + industry_score * 0.2)
        
        return {
            'score': overall_score,
            'school_score': school_score,
            'policy_score': policy_score,
            'industry_score': industry_score,
            'level': self._get_quality_level(overall_score)
        }

    def _calculate_category_score(self, category_result: Dict) -> float:
        """计算类别评分"""
        total = category_result.get('total', 0)
        if total == 0:
            return 0.0
        
        excellent = category_result.get('excellent', 0)
        good = category_result.get('good', 0)
        fair = category_result.get('fair', 0)
        poor = category_result.get('poor', 0)
        
        # 加权计算
        score = (excellent * 1.0 + good * 0.8 + fair * 0.6 + poor * 0.4) / total
        return score

    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 0.8:
            return '优秀'
        elif score >= 0.6:
            return '良好'
        elif score >= 0.4:
            return '一般'
        else:
            return '较差'

    def _save_quality_score(self, data_type: str, data_id: int, score: float):
        """保存质量评分"""
        try:
            conn = sqlite3.connect(self.update_history_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO data_quality_scores
                (data_type, data_id, overall_score, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (data_type, data_id, score, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"保存质量评分失败: {e}")

    def _validate_phone(self, phone: str) -> bool:
        """验证电话号码"""
        import re
        pattern = r'^0\d{2,3}-?\d{7,8}$|^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))

    def _validate_website(self, website: str) -> bool:
        """验证网站URL"""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, website))

    def _validate_date(self, date_str: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False

    def generate_quality_report(self) -> str:
        """生成质量报告"""
        results = self.check_all_data()
        
        report = []
        report.append("=" * 60)
        report.append("数据质量检查报告")
        report.append("=" * 60)
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 总体质量
        report.append("总体质量:")
        report.append(f"  评分: {results['overall']['score']:.2f}")
        report.append(f"  等级: {results['overall']['level']}")
        report.append("")
        
        # 学校数据质量
        report.append("学校数据质量:")
        report.append(f"  总数: {results['school']['total']}")
        report.append(f"  优秀: {results['school']['excellent']}")
        report.append(f"  良好: {results['school']['good']}")
        report.append(f"  一般: {results['school']['fair']}")
        report.append(f"  较差: {results['school']['poor']}")
        report.append(f"  问题数: {len(results['school']['issues'])}")
        report.append("")
        
        # 政策数据质量
        report.append("政策数据质量:")
        report.append(f"  总数: {results['policy']['total']}")
        report.append(f"  优秀: {results['policy']['excellent']}")
        report.append(f"  良好: {results['policy']['good']}")
        report.append(f"  一般: {results['policy']['fair']}")
        report.append(f"  较差: {results['policy']['poor']}")
        report.append(f"  问题数: {len(results['policy']['issues'])}")
        report.append("")
        
        # 问题汇总
        if results['school']['issues'] or results['policy']['issues']:
            report.append("发现的问题:")
            for issue in results['school']['issues'][:10]:
                report.append(f"  - {issue}")
            for issue in results['policy']['issues'][:10]:
                report.append(f"  - {issue}")
            if len(results['school']['issues']) > 10 or len(results['policy']['issues']) > 10:
                report.append(f"  ... 还有 {len(results['school']['issues']) + len(results['policy']['issues']) - 20} 个问题")
        else:
            report.append("未发现明显问题")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)