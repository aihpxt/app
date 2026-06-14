#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统综合测试脚本 - 验证所有核心功能
"""

import os
import sys
import requests
import json

class SystemComprehensiveTest:
    """系统综合测试"""
    
    def __init__(self):
        self.test_results = []
        self.base_url = "http://localhost:8001/api/v1/agent/chat"
    
    def add_result(self, test_name, success, message=""):
        """添加测试结果"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message
        })
    
    def test_database_connection(self):
        """测试数据库连接"""
        print("【1】测试数据库连接...")
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))
            from unified_data_access import get_unified_data_access
            
            dal = get_unified_data_access()
            school_count = dal.get_school_count()
            
            if school_count > 0:
                self.add_result("数据库连接", True, f"数据库正常，包含 {school_count} 所学校")
                print(f"✅ 数据库连接正常，包含 {school_count} 所学校")
            else:
                self.add_result("数据库连接", False, "数据库无数据")
                print("❌ 数据库无数据")
        except Exception as e:
            self.add_result("数据库连接", False, str(e))
            print(f"❌ 数据库连接失败: {e}")
    
    def test_school_query(self):
        """测试学校查询功能"""
        print("\n【2】测试学校查询功能...")
        try:
            from unified_data_access import get_unified_data_access
            
            dal = get_unified_data_access()
            
            # 测试搜索学校
            results = dal.search_schools("师大附中")
            if results:
                self.add_result("学校搜索", True, f"找到 {len(results)} 所学校")
                print(f"✅ 学校搜索正常: 找到 {len(results)} 所学校")
            else:
                self.add_result("学校搜索", False, "未找到学校")
                print("❌ 学校搜索失败")
            
            # 测试获取学校信息
            school = dal.get_school_by_name("云南师范大学附属中学")
            if school:
                self.add_result("学校详情", True, school['name'])
                print(f"✅ 获取学校详情正常: {school['name']}")
            else:
                self.add_result("学校详情", False, "未找到学校详情")
                print("❌ 获取学校详情失败")
            
            # 测试获取地州学校列表
            schools = dal.get_schools_by_prefecture("昆明市")
            if schools:
                self.add_result("地州学校列表", True, f"昆明市有 {len(schools)} 所学校")
                print(f"✅ 获取地州学校列表正常: 昆明市有 {len(schools)} 所学校")
            else:
                self.add_result("地州学校列表", False, "未找到地州学校")
                print("❌ 获取地州学校列表失败")
        except Exception as e:
            self.add_result("学校查询功能", False, str(e))
            print(f"❌ 学校查询功能失败: {e}")
    
    def test_policy_query(self):
        """测试政策查询功能"""
        print("\n【3】测试政策查询功能...")
        try:
            from unified_data_access import get_unified_data_access
            
            dal = get_unified_data_access()
            
            # 测试获取政策
            policy = dal.get_policy_by_prefecture("km")
            if policy:
                self.add_result("政策查询", True, "获取政策成功")
                print("✅ 政策查询正常")
            else:
                self.add_result("政策查询", False, "未找到政策")
                print("❌ 政策查询失败")
            
            # 测试获取所有地州
            prefectures = dal.get_all_prefectures()
            if prefectures:
                self.add_result("地州列表", True, f"获取到 {len(prefectures)} 个地州")
                print(f"✅ 获取地州列表正常: {len(prefectures)} 个地州")
            else:
                self.add_result("地州列表", False, "未获取到地州列表")
                print("❌ 获取地州列表失败")
        except Exception as e:
            self.add_result("政策查询功能", False, str(e))
            print(f"❌ 政策查询功能失败: {e}")
    
    def test_api_interface(self):
        """测试API接口"""
        print("\n【4】测试API接口...")
        test_cases = [
            ("师大附中怎么样", "测试学校查询"),
            ("昆明有哪些高中", "测试地州学校搜索"),
            ("文山州中考政策", "测试政策查询"),
            ("650分能上什么学校", "测试分数分析"),
            ("如何预约参观学校", "测试预约咨询"),
        ]
        
        session_id = "comprehensive_test"
        
        for question, description in test_cases:
            try:
                r = requests.post(self.base_url, json={
                    'message': question,
                    'agent_id': 'zk-master',
                    'session_id': session_id
                }, timeout=15)
                
                if r.status_code == 200:
                    response = r.json().get('response', '')
                    if response:
                        self.add_result(description, True, "响应正常")
                        print(f"✅ {description}: 响应正常")
                    else:
                        self.add_result(description, False, "响应为空")
                        print(f"❌ {description}: 响应为空")
                else:
                    self.add_result(description, False, f"HTTP {r.status_code}")
                    print(f"❌ {description}: HTTP {r.status_code}")
            except Exception as e:
                self.add_result(description, False, str(e))
                print(f"❌ {description}: {e}")
    
    def test_context_management(self):
        """测试上下文管理"""
        print("\n【5】测试上下文管理...")
        try:
            session_id = "context_test_session"
            
            # 第一轮：询问学校
            r1 = requests.post(self.base_url, json={
                'message': "我想了解师大附中",
                'agent_id': 'zk-master',
                'session_id': session_id
            }, timeout=10)
            
            if r1.status_code != 200:
                self.add_result("上下文管理", False, "第一轮请求失败")
                print("❌ 上下文管理失败")
                return
            
            # 第二轮：追问分数线（应该保持上下文）
            r2 = requests.post(self.base_url, json={
                'message': "它的分数线是多少",
                'agent_id': 'zk-master',
                'session_id': session_id
            }, timeout=10)
            
            if r2.status_code == 200:
                response = r2.json().get('response', '')
                if "680" in response or "分数线" in response:
                    self.add_result("上下文管理", True, "上下文保持正常")
                    print("✅ 上下文管理正常")
                else:
                    self.add_result("上下文管理", False, "上下文丢失")
                    print("❌ 上下文丢失")
            else:
                self.add_result("上下文管理", False, "第二轮请求失败")
                print("❌ 上下文管理失败")
        except Exception as e:
            self.add_result("上下文管理", False, str(e))
            print(f"❌ 上下文管理失败: {e}")
    
    def test_data_integrity(self):
        """测试数据完整性"""
        print("\n【6】测试数据完整性...")
        try:
            from unified_data_access import get_unified_data_access
            
            dal = get_unified_data_access()
            all_schools = []
            
            for prefecture in dal.get_all_prefectures():
                schools = dal.get_schools_by_prefecture(prefecture)
                all_schools.extend(schools)
            
            # 检查必填字段（适配数据库实际字段结构）
            valid_count = 0
            invalid_count = 0
            
            for school in all_schools:
                # 数据库中实际使用的字段名
                required_fields = ['name', 'type_name', 'address', 'min_score']
                missing = []
                for f in required_fields:
                    value = school.get(f)
                    if value is None or value == '' or value == 0:
                        missing.append(f)
                if missing:
                    invalid_count += 1
                else:
                    valid_count += 1
            
            self.add_result("数据完整性", True, f"有效: {valid_count}, 无效: {invalid_count}")
            print(f"✅ 数据完整性检查完成: 有效 {valid_count} 条, 无效 {invalid_count} 条")
            
            # 计算数据完整率（95%以上视为合格）
            completeness_rate = (valid_count / len(all_schools)) * 100
            
            if completeness_rate >= 95:
                self.add_result("数据质量", True, f"数据完整率 {completeness_rate:.1f}%，符合要求")
                print(f"✅ 数据质量合格，完整率 {completeness_rate:.1f}%")
            else:
                self.add_result("数据质量", False, f"数据完整率 {completeness_rate:.1f}%，低于95%")
                print(f"⚠️ 数据质量不合格，完整率 {completeness_rate:.1f}%")
        except Exception as e:
            self.add_result("数据完整性", False, str(e))
            print(f"❌ 数据完整性检查失败: {e}")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("系统综合测试报告")
        print("=" * 80)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        print(f"\n测试总数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"通过率: {(passed/total)*100:.1f}%")
        
        print("\n详细结果:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test_name']}: {result['message']}")
        
        if failed == 0:
            print("\n🎉 所有测试通过！系统运行正常！")
        else:
            print(f"\n⚠️ 有 {failed} 项测试未通过，请检查错误信息")
        
        return failed == 0
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("系统综合测试")
        print("=" * 80)
        
        self.test_database_connection()
        self.test_school_query()
        self.test_policy_query()
        self.test_api_interface()
        self.test_context_management()
        self.test_data_integrity()
        
        return self.generate_report()

if __name__ == "__main__":
    tester = SystemComprehensiveTest()
    tester.run_all_tests()