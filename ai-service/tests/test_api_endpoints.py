#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点集成测试
测试所有核心API端点的功能和响应
"""

import pytest
from fastapi.testclient import TestClient
import math

# 确保智能体注册
from agents.agent_registration import register_all_agents
register_all_agents()

# 导入FastAPI应用
from app.core.app import app


class TestHealthEndpoint:
    """健康检查端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_health_check(self):
        """测试健康检查端点返回200和正确结构"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "data" in data
        assert "status" in data["data"]
        assert "system" in data["data"]


class TestDashboardEndpoint:
    """Dashboard监控端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_dashboard_returns_200(self):
        """测试Dashboard端点返回200"""
        response = self.client.get("/api/monitor/dashboard")

        assert response.status_code == 200

    def test_dashboard_response_structure(self):
        """测试Dashboard返回正确的数据结构"""
        response = self.client.get("/api/monitor/dashboard")
        data = response.json()

        assert data.get("success") == True
        assert "data" in data

    def test_dashboard_no_inf_values(self):
        """测试Dashboard返回数据不包含inf/nan值"""
        response = self.client.get("/api/monitor/dashboard")
        data = response.json()

        # 递归检查数据中不包含inf或nan
        def check_no_inf(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_inf(v)
            elif isinstance(obj, list):
                for item in obj:
                    check_no_inf(item)
            elif isinstance(obj, float):
                assert not (math.isinf(obj) or math.isnan(obj)), f"Found inf/nan value: {obj}"

        if "data" in data:
            check_no_inf(data["data"])


class TestSchoolsEndpoint:
    """学校列表端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_schools_list_v1(self):
        """测试学校列表v1端点返回200"""
        response = self.client.get("/api/v1/schools")

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_schools_list_returns_data(self):
        """测试学校列表返回数据"""
        response = self.client.get("/api/v1/schools")
        data = response.json()

        assert "data" in data
        assert isinstance(data["data"], (list, dict))


class TestPoliciesEndpoint:
    """政策列表端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_policies_list(self):
        """测试政策列表端点返回200"""
        response = self.client.get("/api/v1/policies")

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_policies_list_returns_data(self):
        """测试政策列表返回数据"""
        response = self.client.get("/api/v1/policies")
        data = response.json()

        assert "data" in data
        assert isinstance(data["data"], (list, dict))


class TestArticlesEndpoint:
    """文章列表端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_articles_list(self):
        """测试文章列表端点返回200"""
        response = self.client.get("/api/v1/articles")

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_articles_list_returns_data(self):
        """测试文章列表返回数据"""
        response = self.client.get("/api/v1/articles")
        data = response.json()

        assert "data" in data


class TestAIChatEndpoint:
    """AI对话端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_ai_chat_basic(self):
        """测试AI对话端点基本功能"""
        response = self.client.post(
            "/ai/chat",
            json={"message": "你好", "user_id": "test_user"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_ai_chat_returns_content(self):
        """测试AI对话返回内容"""
        response = self.client.post(
            "/ai/chat",
            json={"message": "昆明一中怎么样", "user_id": "test_user"}
        )
        data = response.json()

        assert "data" in data or "content" in data


class TestRootEndpoint:
    """根路径端点测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.client = TestClient(app)

    def test_root(self):
        """测试根路径返回欢迎信息"""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "message" in data["data"]
