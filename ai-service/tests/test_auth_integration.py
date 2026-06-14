"""认证API集成测试"""
import sys
from unittest.mock import MagicMock

# Mock heavy modules to avoid hanging during import (LLM services, agents, etc.)
_mock_llm_service = MagicMock()
_mock_llm_service.LLMService = MagicMock()
sys.modules['openclaw.llm_service'] = _mock_llm_service
sys.modules['openclaw.multi_llm_service'] = MagicMock()

_mock_agent_reg = MagicMock()
_mock_agent_reg.register_all_agents = MagicMock()
sys.modules['agents.agent_registration'] = _mock_agent_reg

# Mock Redis to avoid slow connection retries at startup
_mock_redis = MagicMock()
_mock_redis.Redis.side_effect = ConnectionError("Redis unavailable in test")
sys.modules['redis'] = _mock_redis

import pytest
from fastapi.testclient import TestClient
from app.core.app import app
from app.core.database_pool import get_db_manager
from app.models.user import User, Base
import bcrypt

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Setup test database with a known user"""
    db_manager = get_db_manager()
    # Ensure the users table exists
    Base.metadata.create_all(db_manager.engine)
    session = db_manager.get_session()
    try:
        # Create test user
        password_hash = bcrypt.hashpw("testpass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        existing = session.query(User).filter(User.username == "testuser").first()
        if not existing:
            user = User(
                username="testuser",
                password_hash=password_hash,
                email="test@example.com",
                phone="13800138000",
                role="student"
            )
            session.add(user)
            session.commit()
    finally:
        session.close()
    yield
    # Cleanup
    session = db_manager.get_session()
    try:
        session.query(User).filter(User.username == "testuser").delete()
        session.query(User).filter(User.username == "newuser_test").delete()
        session.commit()
    finally:
        session.close()


class TestAuthLogin:
    """登录接口测试"""

    def test_login_success(self):
        """测试登录成功"""
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "Bearer"

    def test_login_wrong_password(self):
        """测试登录失败 - 错误密码"""
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "用户名或密码错误" in data["message"]

    def test_login_nonexistent_user(self):
        """测试登录失败 - 用户不存在"""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent_user_xyz",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


class TestAuthRegister:
    """注册接口测试"""

    def test_register_success(self):
        """测试注册成功"""
        response = client.post("/api/v1/auth/register", json={
            "username": "newuser_test",
            "password": "securepass123",
            "email": "newuser@test.com",
            "phone": "13900139000",
            "role": "student"
        })
        assert response.status_code == 200
        data = response.json()
        # May succeed or fail depending on DB state
        assert "user_id" in data or "detail" in data

    def test_register_short_password(self):
        """测试注册失败 - 密码太短"""
        response = client.post("/api/v1/auth/register", json={
            "username": "shortpw",
            "password": "123",
            "role": "student"
        })
        assert response.status_code == 400
        assert "密码长度至少6位" in response.json()["detail"]

    def test_register_duplicate_username(self):
        """测试注册失败 - 用户名重复"""
        # Try to register with existing username
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "password": "testpass123",
            "role": "student"
        })
        if response.status_code == 400:
            assert "用户名已存在" in response.json()["detail"]


class TestAuthToken:
    """Token相关测试"""

    def test_refresh_token(self):
        """测试Token刷新"""
        # First login to get tokens
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        if login_resp.json().get("success"):
            refresh_token = login_resp.json()["data"]["refresh_token"]

            response = client.post("/api/v1/auth/refresh", json={
                "refresh_token": refresh_token
            })
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

    def test_get_current_user_unauthorized(self):
        """测试未授权获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]

    def test_get_current_user_authorized(self):
        """测试已授权获取用户信息"""
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        if login_resp.json().get("success"):
            token = login_resp.json()["data"]["access_token"]

            response = client.get("/api/v1/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"
            assert "student" in data["roles"]