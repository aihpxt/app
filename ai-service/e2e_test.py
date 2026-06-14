#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E全域测试脚本 - 完整版
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
import json
from datetime import datetime

class E2ETester:
    def __init__(self, base_url="http://127.0.0.1:8001"):
        self.base_url = base_url
        self.results = []
        self.start_time = time.time()
        self.token = None

    def test_endpoint(self, method, endpoint, data=None, expected_status=200, headers=None):
        """测试单个API接口"""
        url = f"{self.base_url}{endpoint}"
        test_name = f"{method} {endpoint}"

        if headers is None:
            headers = {}
        
        if self.token and not headers.get('Authorization'):
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=30, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=30, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=30, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            actual_status = response.status_code
            success = actual_status == expected_status

            result = {
                "test_name": test_name,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "success": success,
                "response_time": response.elapsed.total_seconds(),
                "timestamp": datetime.now().isoformat()
            }

            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text[:200]

            if not success:
                result["error"] = f"Expected {expected_status}, got {actual_status}"

            self.results.append(result)
            print(f"{'✓' if success else '✗'} {test_name} - Status: {actual_status}, Time: {result['response_time']:.3f}s")

        except Exception as e:
            result = {
                "test_name": test_name,
                "expected_status": expected_status,
                "actual_status": "Error",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            print(f"✗ {test_name} - Error: {str(e)}")

        return result

    def run_root_tests(self):
        """测试根路径接口"""
        print("\n=== 根路径测试 ===")
        self.test_endpoint("GET", "/")

    def run_health_tests(self):
        """运行健康检查相关测试"""
        print("\n=== 健康检查接口测试 ===")
        self.test_endpoint("GET", "/health")
        self.test_endpoint("GET", "/health/metrics")
        self.test_endpoint("GET", "/health/services")
        self.test_endpoint("GET", "/health/cache")
        self.test_endpoint("GET", "/health/tasks")

    def run_auth_tests(self):
        """运行认证测试"""
        print("\n=== 认证接口测试 ===")
        
        # 使用预设的测试账号登录
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        result = self.test_endpoint("POST", "/api/v1/auth/login", data=login_data)
        
        if result.get('success') and result.get('actual_status') == 200:
            try:
                resp_data = result.get('response_data', {})
                # 直接获取access_token
                if isinstance(resp_data, dict) and 'access_token' in resp_data:
                    self.token = resp_data.get('access_token')
                    if self.token:
                        print(f"  ✓ 成功获取Token: {self.token[:20]}...")
            except Exception as e:
                print(f"  ! 解析响应失败: {e}")
        
        # 测试获取当前用户信息（需要token）
        if self.token:
            self.test_endpoint("GET", "/api/v1/auth/me")

    def run_agent_tests(self):
        """运行智能体相关测试"""
        print("\n=== 智能体接口测试 ===")
        
        # 获取所有智能体
        self.test_endpoint("GET", "/api/v1/agents")
        
        # 测试智能体聊天
        chat_data = {
            "input": "昆明有哪些好的高中？",
            "agent_id": "zk-master",
            "context": {}
        }
        result = self.test_endpoint("POST", "/api/v1/agent/chat", data=chat_data)
        
        if result.get('success') and 'response_data' in result:
            resp = result['response_data']
            if resp.get('success') and 'data' in resp:
                print(f"  ✓ 智能体响应: {str(resp['data'])[:100]}...")

    def run_utils_tests(self):
        """运行工具接口测试"""
        print("\n=== 工具接口测试 ===")
        
        # 工具路由可能在不同位置
        # 先测试健康检查已经做了
        
        # 测试UUID生成
        self.test_endpoint("GET", "/api/utils/string/uuid")
        
        # 测试时间接口
        self.test_endpoint("GET", "/api/utils/time/current")
        
        # 测试邮箱验证
        validate_data = {"email": "test@example.com"}
        self.test_endpoint("POST", "/api/utils/validate/email", data=validate_data)

    def run_cache_tests(self):
        """运行缓存指标测试"""
        print("\n=== 缓存指标测试 ===")
        self.test_endpoint("GET", "/api/v1/cache/stats")
        self.test_endpoint("GET", "/api/v1/cache/health")
        self.test_endpoint("GET", "/api/v1/cache/report")

    def run_prometheus_tests(self):
        """运行Prometheus监控测试"""
        print("\n=== Prometheus监控测试 ===")
        self.test_endpoint("GET", "/api/metrics/prometheus")
        self.test_endpoint("GET", "/api/metrics/summary")

    def run_audit_tests(self):
        """运行审计日志测试"""
        print("\n=== 审计日志测试 ===")
        self.test_endpoint("GET", "/api/audit/logs")

    def run_alerts_tests(self):
        """运行告警测试"""
        print("\n=== 告警系统测试 ===")
        self.test_endpoint("GET", "/api/alerts/")
        self.test_endpoint("GET", "/api/alerts/check")

    def run_performance_tests(self):
        """运行性能测试"""
        print("\n=== 性能指标测试 ===")
        self.test_endpoint("GET", "/api/performance/")
        self.test_endpoint("GET", "/api/performance/cache/stats")
        self.test_endpoint("GET", "/api/performance/recommendations")

    def run_tasks_tests(self):
        """运行任务调度测试"""
        print("\n=== 任务调度测试 ===")
        # tasks路由需要特殊处理，暂时跳过

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("云南省AI择校平台 - E2E全域测试")
        print(f"测试时间: {datetime.now().isoformat()}")
        print(f"测试目标: {self.base_url}")
        print("=" * 70)

        # 基础API测试
        self.run_root_tests()
        self.run_health_tests()
        
        # 系统功能测试
        self.run_utils_tests()
        self.run_cache_tests()
        self.run_prometheus_tests()
        self.run_performance_tests()
        
        # 业务功能测试
        self.run_agent_tests()
        
        # 安全相关测试
        self.run_auth_tests()
        self.run_audit_tests()
        self.run_alerts_tests()

        # 生成测试报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        elapsed_time = time.time() - self.start_time

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        avg_response_time = sum(r['response_time'] for r in self.results if 'response_time' in r) / len(self.results) if self.results else 0
        
        # 计算响应时间统计
        response_times = [r['response_time'] for r in self.results if 'response_time' in r]
        min_response = min(response_times) if response_times else 0
        max_response = max(response_times) if response_times else 0

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": f"{pass_rate:.2f}%",
                "avg_response_time": f"{avg_response_time:.3f}s",
                "min_response_time": f"{min_response:.3f}s",
                "max_response_time": f"{max_response:.3f}s",
                "total_time": f"{elapsed_time:.2f}s"
            },
            "test_results": self.results,
            "timestamp": datetime.now().isoformat()
        }

        # 保存报告到文件
        report_file = f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 70)
        print("测试报告摘要")
        print("=" * 70)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {pass_rate:.2f}%")
        print(f"\n响应时间统计:")
        print(f"  平均: {avg_response_time:.3f}s")
        print(f"  最小: {min_response:.3f}s")
        print(f"  最大: {max_response:.3f}s")
        print(f"总耗时: {elapsed_time:.2f}s")
        print(f"\n详细报告已保存到: {report_file}")
        print("=" * 70)
        
        # 显示失败的测试详情
        if failed_tests > 0:
            print("\n失败的测试详情:")
            print("-" * 70)
            for result in self.results:
                if not result['success']:
                    print(f"✗ {result['test_name']}")
                    print(f"  错误: {result.get('error', 'N/A')}")
                    print(f"  时间: {result.get('timestamp', 'N/A')}")

        return report

if __name__ == "__main__":
    tester = E2ETester()
    tester.run_all_tests()
