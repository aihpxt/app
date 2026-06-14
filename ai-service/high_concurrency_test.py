#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高并发测试脚本
用于测试系统的并发处理能力和稳定性
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys

class HighConcurrencyTester:
    def __init__(self, base_url="http://127.0.0.1:8001", num_requests=100, max_workers=20):
        self.base_url = base_url
        self.num_requests = num_requests
        self.max_workers = max_workers
        self.results = []
        self.start_time = None
        self.end_time = None

    def test_single_request(self, request_id):
        """测试单个请求"""
        url = f"{self.base_url}/api/v1/agents/chat"

        test_questions = [
            "昆明有哪些好高中？",
            "分数650分能上什么学校？",
            "2026年中考政策有哪些变化？",
            "如何填报志愿？",
            "未央中学怎么样？",
            "昆明一中录取分数线是多少？",
            "中考志愿填报技巧有哪些？",
            "如何选择合适的高中？",
            "云南中考政策解读",
            "高中学校对比分析"
        ]

        question = test_questions[request_id % len(test_questions)]

        try:
            start = time.time()
            response = requests.post(
                url,
                json={"question": question},
                timeout=10
            )
            elapsed = time.time() - start

            result = {
                "request_id": request_id,
                "question": question,
                "status_code": response.status_code,
                "response_time": elapsed,
                "success": response.status_code == 200,
                "error": None,
                "timestamp": datetime.now().isoformat()
            }

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    result["error"] = error_data.get("detail", error_data.get("error", str(response.status_code)))
                except:
                    result["error"] = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            result = {
                "request_id": request_id,
                "question": question,
                "status_code": "Timeout",
                "response_time": 10.0,
                "success": False,
                "error": "Request timeout",
                "timestamp": datetime.now().isoformat()
            }

        except requests.exceptions.ConnectionError as e:
            result = {
                "request_id": request_id,
                "question": question,
                "status_code": "ConnectionError",
                "response_time": 0.0,
                "success": False,
                "error": f"Connection error: {str(e)[:50]}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            result = {
                "request_id": request_id,
                "question": question,
                "status_code": "Error",
                "response_time": 0.0,
                "success": False,
                "error": str(e)[:100],
                "timestamp": datetime.now().isoformat()
            }

        return result

    def run_concurrent_test(self):
        """运行并发测试"""
        print("=" * 80)
        print("高并发测试开始")
        print("=" * 80)
        print(f"测试参数:")
        print(f"  - 目标URL: {self.base_url}")
        print(f"  - 请求数量: {self.num_requests}")
        print(f"  - 并发数: {self.max_workers}")
        print(f"  - 开始时间: {datetime.now().isoformat()}")
        print("=" * 80)

        self.start_time = time.time()

        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有请求
            futures = {
                executor.submit(self.test_single_request, i): i
                for i in range(self.num_requests)
            }

            # 收集结果
            for future in as_completed(futures):
                request_id = futures[future]
                try:
                    result = future.result()
                    self.results.append(result)

                    # 每10个请求打印一次进度
                    if (len(self.results) % 10 == 0):
                        print(f"进度: {len(self.results)}/{self.num_requests} 请求已完成")

                except Exception as e:
                    print(f"请求 {request_id} 执行失败: {e}")
                    self.results.append({
                        "request_id": request_id,
                        "success": False,
                        "error": str(e)
                    })

        self.end_time = time.time()

    def generate_report(self):
        """生成测试报告"""
        total_time = self.end_time - self.start_time
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.get("success"))
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

        # 计算响应时间统计
        response_times = [r.get("response_time", 0) for r in self.results if r.get("success")]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0

        # 计算吞吐量
        throughput = total_requests / total_time if total_time > 0 else 0

        # 统计错误类型
        error_stats = {}
        for result in self.results:
            if not result.get("success"):
                error_type = result.get("error", "Unknown error")
                # 确保error_type是字符串类型
                if isinstance(error_type, dict):
                    error_type = str(error_type)
                elif not isinstance(error_type, str):
                    error_type = str(error_type)
                if error_type not in error_stats:
                    error_stats[error_type] = 0
                error_stats[error_type] += 1

        # 生成报告
        report = {
            "test_summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": f"{success_rate:.2f}%",
                "total_time": f"{total_time:.2f}s",
                "throughput": f"{throughput:.2f} req/s",
                "avg_response_time": f"{avg_response_time:.3f}s",
                "min_response_time": f"{min_response_time:.3f}s",
                "max_response_time": f"{max_response_time:.3f}s"
            },
            "error_stats": error_stats,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }

        # 打印报告
        print("\n" + "=" * 80)
        print("测试报告")
        print("=" * 80)
        print(f"总请求数: {total_requests}")
        print(f"成功请求: {successful_requests} ✓")
        print(f"失败请求: {failed_requests} ✗")
        print(f"成功率: {success_rate:.2f}%")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"吞吐量: {throughput:.2f} 请求/秒")
        print(f"平均响应时间: {avg_response_time:.3f}秒")
        print(f"最小响应时间: {min_response_time:.3f}秒")
        print(f"最大响应时间: {max_response_time:.3f}秒")

        if error_stats:
            print("\n错误统计:")
            for error_type, count in error_stats.items():
                print(f"  - {error_type}: {count}次")

        # 验收标准检查
        print("\n" + "=" * 80)
        print("验收标准检查")
        print("=" * 80)

        checks = [
            ("成功率 >= 95%", success_rate >= 95, f"{success_rate:.2f}%"),
            ("平均响应时间 < 1秒", avg_response_time < 1.0, f"{avg_response_time:.3f}秒"),
            ("总耗时 < 60秒", total_time < 60, f"{total_time:.2f}秒"),
        ]

        all_passed = True
        for check_name, passed, value in checks:
            status = "✓ 通过" if passed else "✗ 未通过"
            print(f"{status} - {check_name}: {value}")
            if not passed:
                all_passed = False

        print("=" * 80)

        if all_passed:
            print("🎉 所有测试通过！系统在高并发场景下表现良好。")
        else:
            print("⚠️ 部分测试未通过，需要进一步优化。")

        # 保存报告到文件
        report_file = f"high_concurrency_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n详细报告已保存到: {report_file}")

        return report

def main():
    """主函数"""
    # 创建高并发测试器
    tester = HighConcurrencyTester(
        base_url="http://127.0.0.1:8001",
        num_requests=100,  # 100个请求
        max_workers=20     # 20个并发
    )

    # 运行测试
    tester.run_concurrent_test()

    # 生成报告
    report = tester.generate_report()

    # 返回退出码
    success_rate = report["test_summary"]["success_rate"]
    if "%" in success_rate:
        success_rate = float(success_rate.replace("%", ""))

    return 0 if success_rate >= 95 else 1

if __name__ == "__main__":
    sys.exit(main())
