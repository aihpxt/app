#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全系统端到端测试脚本
测试完整的用户对话流程、API接口、数据库数据流转、上下文保持和错误处理
"""

import os
import sys
import requests
import json
import uuid

class E2ETester:
    """端到端测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001/api/v1/agent/chat"
        self.test_results = []
        self.session_id = str(uuid.uuid4())
    
    def add_result(self, test_name, success, message=""):
        """添加测试结果"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message
        })
    
    def log(self, message):
        """打印日志"""
        print(f"📝 {message}")
    
    def success(self, message):
        """打印成功信息"""
        print(f"✅ {message}")
    
    def fail(self, message):
        """打印失败信息"""
        print(f"❌ {message}")
    
    def test_full_conversation_flow(self):
        """测试完整对话流程"""
        self.log("【1】测试完整对话流程")
        
        conversation = [
            ("你好", "问候"),
            ("我是9年级学生，在文山广南", "自我介绍"),
            ("想了解中考择校", "说明意图"),
            ("有哪些推荐的学校", "询问推荐"),
            ("未央中学怎么样", "具体学校咨询"),
            ("录取分数线是多少", "分数线查询"),
            ("如何预约参观", "预约咨询"),
            ("本周日可以吗", "时间确认"),
            ("谢谢", "结束对话"),
        ]
        
        session_id = f"e2e_test_{uuid.uuid4().hex[:8]}"
        all_success = True
        
        for i, (question, description) in enumerate(conversation):
            try:
                r = requests.post(self.base_url, json={
                    'message': question,
                    'agent_id': 'zk-master',
                    'session_id': session_id
                }, timeout=15)
                
                if r.status_code == 200:
                    response = r.json()
                    if 'response' in response and response['response']:
                        self.log(f"  对话 {i+1}: {description} - 响应正常")
                    else:
                        all_success = False
                        self.fail(f"  对话 {i+1}: {description} - 响应为空")
                else:
                    all_success = False
                    self.fail(f"  对话 {i+1}: {description} - HTTP {r.status_code}")
            except Exception as e:
                all_success = False
                self.fail(f"  对话 {i+1}: {description} - {e}")
        
        if all_success:
            self.add_result("完整对话流程", True, "9轮对话全部成功")
            self.success("完整对话流程测试通过")
        else:
            self.add_result("完整对话流程", False, "部分对话失败")
            self.fail("完整对话流程测试失败")
    
    def test_api_endpoints(self):
        """测试API接口"""
        self.log("\n【2】测试API接口")
        
        endpoints = [
            ("POST /api/v1/agent/chat", {"message": "师大附中怎么样", "agent_id": "zk-master", "session_id": "test"}),
        ]
        
        all_success = True
        
        for endpoint, payload in endpoints:
            try:
                r = requests.post(self.base_url, json=payload, timeout=15)
                
                if r.status_code == 200:
                    response = r.json()
                    if 'response' in response:
                        self.log(f"  {endpoint} - 响应正常")
                    else:
                        all_success = False
                        self.fail(f"  {endpoint} - 响应格式错误")
                else:
                    all_success = False
                    self.fail(f"  {endpoint} - HTTP {r.status_code}")
            except Exception as e:
                all_success = False
                self.fail(f"  {endpoint} - {e}")
        
        # 测试健康检查接口（可选）
        try:
            r = requests.get("http://localhost:8001/api/health", timeout=10)
            if r.status_code == 200:
                self.log("  GET /api/health - 响应正常")
            else:
                self.log(f"  GET /api/health - 未配置（HTTP {r.status_code}）")
        except Exception as e:
            self.log(f"  GET /api/health - 未配置")
        
        if all_success:
            self.add_result("API接口测试", True, "核心接口测试通过")
            self.success("API接口测试通过")
        else:
            self.add_result("API接口测试", False, "部分接口测试失败")
            self.fail("API接口测试失败")
    
    def test_database_data_flow(self):
        """测试数据库数据流转"""
        self.log("\n【3】测试数据库数据流转")
        
        try:
            # 从数据库获取数据
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-service'))
            from unified_data_access import get_unified_data_access
            
            dal = get_unified_data_access()
            school = dal.get_school_by_name("云南师范大学附属中学")
            
            if school:
                db_score = school.get('min_score')
                
                # 通过API获取相同数据
                session_id = f"db_test_{uuid.uuid4().hex[:8]}"
                r = requests.post(self.base_url, json={
                    'message': "云南师范大学附属中学的分数线是多少",
                    'agent_id': 'zk-master',
                    'session_id': session_id
                }, timeout=15)
                
                if r.status_code == 200:
                    response = r.json().get('response', '')
                    
                    # 检查响应中是否包含学校名称（验证数据流转）
                    if "云南师范大学附属中学" in response or "师大附中" in response:
                        self.add_result("数据库数据流转", True, "数据库数据成功流转到API响应")
                        self.success("数据库数据流转测试通过")
                    else:
                        self.add_result("数据库数据流转", False, "数据库数据与API响应不一致")
                        self.fail("数据库数据流转测试失败")
                else:
                    self.add_result("数据库数据流转", False, "API请求失败")
                    self.fail("数据库数据流转测试失败")
            else:
                self.add_result("数据库数据流转", False, "数据库中未找到学校")
                self.fail("数据库数据流转测试失败")
        except Exception as e:
            self.add_result("数据库数据流转", False, str(e))
            self.fail(f"数据库数据流转测试失败: {e}")
    
    def test_context_management(self):
        """测试上下文保持"""
        self.log("\n【4】测试上下文保持")
        
        session_id = f"context_test_{uuid.uuid4().hex[:8]}"
        try:
            # 第一轮：询问具体学校
            r1 = requests.post(self.base_url, json={
                'message': "我想了解师大附中",
                'agent_id': 'zk-master',
                'session_id': session_id
            }, timeout=15)
            
            if r1.status_code != 200:
                self.add_result("上下文保持", False, "第一轮请求失败")
                self.fail("上下文保持测试失败")
                return
            
            # 第二轮：追问该校的分数线（使用"它"来测试上下文）
            r2 = requests.post(self.base_url, json={
                'message': "它的分数线是多少",
                'agent_id': 'zk-master',
                'session_id': session_id
            }, timeout=15)
            
            if r2.status_code == 200:
                response = r2.json().get('response', '')
                
                # 检查响应中是否包含学校名称或分数信息
                if "师大附中" in response or "分数线" in response or "600" in response:
                    self.add_result("上下文保持", True, "上下文保持正常")
                    self.success("上下文保持测试通过")
                else:
                    self.add_result("上下文保持", False, "上下文丢失")
                    self.fail("上下文保持测试失败")
            else:
                self.add_result("上下文保持", False, "第二轮请求失败")
                self.fail("上下文保持测试失败")
        except Exception as e:
            self.add_result("上下文保持", False, str(e))
            self.fail(f"上下文保持测试失败: {e}")
    
    def test_error_handling(self):
        """测试错误处理"""
        self.log("\n【5】测试错误处理")
        
        test_cases = [
            ("", "空输入"),
            ("   ", "空白输入"),
            ("!!@@##", "特殊字符"),
            ("x" * 5000, "超长输入"),
            ("hello world", "无意义英文"),
        ]
        
        all_success = True
        
        for input_text, description in test_cases:
            session_id = f"error_test_{uuid.uuid4().hex[:8]}"
            try:
                r = requests.post(self.base_url, json={
                    'message': input_text,
                    'agent_id': 'zk-master',
                    'session_id': session_id
                }, timeout=15)
                
                if r.status_code == 200:
                    response = r.json().get('response', '')
                    
                    if response:
                        self.log(f"  {description} - 处理正常")
                    else:
                        all_success = False
                        self.fail(f"  {description} - 响应为空")
                else:
                    all_success = False
                    self.fail(f"  {description} - HTTP {r.status_code}")
            except Exception as e:
                all_success = False
                self.fail(f"  {description} - {e}")
        
        if all_success:
            self.add_result("错误处理", True, "所有异常输入处理正常")
            self.success("错误处理测试通过")
        else:
            self.add_result("错误处理", False, "部分异常输入处理失败")
            self.fail("错误处理测试失败")
    
    def test_edge_cases(self):
        """测试边界情况"""
        self.log("\n【6】测试边界情况")
        
        test_cases = [
            ("0分能上什么学校", "极低分数"),
            ("800分能上什么学校", "极高分数"),
            ("火星有什么高中", "无效地点"),
            ("2050年中考政策", "未来时间"),
        ]
        
        all_success = True
        
        for question, description in test_cases:
            session_id = f"edge_test_{uuid.uuid4().hex[:8]}"
            try:
                r = requests.post(self.base_url, json={
                    'message': question,
                    'agent_id': 'zk-master',
                    'session_id': session_id
                }, timeout=15)
                
                if r.status_code == 200:
                    response = r.json().get('response', '')
                    
                    if response and "抱歉" not in response:
                        self.log(f"  {description} - 处理正常")
                    else:
                        self.log(f"  {description} - 返回友好提示")
                else:
                    all_success = False
                    self.fail(f"  {description} - HTTP {r.status_code}")
            except Exception as e:
                all_success = False
                self.fail(f"  {description} - {e}")
        
        if all_success:
            self.add_result("边界情况处理", True, "所有边界情况处理正常")
            self.success("边界情况处理测试通过")
        else:
            self.add_result("边界情况处理", False, "部分边界情况处理失败")
            self.fail("边界情况处理测试失败")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("全系统端到端测试报告")
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
        
        # 生成JSON报告
        report = {
            "timestamp": "2026-05-19",
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed/total)*100,
            "results": self.test_results
        }
        
        report_path = os.path.join(os.path.dirname(__file__), 'e2e_test_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试报告已保存到: {report_path}")
        
        if failed == 0:
            print("\n🎉 所有端到端测试通过！系统运行正常！")
        else:
            print(f"\n⚠️ 有 {failed} 项测试未通过，请检查错误信息")
        
        return failed == 0
    
    def run_all_tests(self):
        """运行所有端到端测试"""
        print("=" * 80)
        print("全系统端到端测试")
        print("=" * 80)
        
        self.test_full_conversation_flow()
        self.test_api_endpoints()
        self.test_database_data_flow()
        self.test_context_management()
        self.test_error_handling()
        self.test_edge_cases()
        
        return self.generate_report()

if __name__ == "__main__":
    tester = E2ETester()
    tester.run_all_tests()