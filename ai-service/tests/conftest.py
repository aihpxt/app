"""
pytest测试配置文件
提供全局测试夹具和配置
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def data_dir():
    """返回数据目录"""
    return project_root / "data"


@pytest.fixture(scope="function")
def mock_cache():
    """提供模拟缓存实例"""
    from app.core.cache import Cache
    cache = Cache(maxsize=100, ttl=60)
    yield cache
    cache.clear()


@pytest.fixture(scope="function")
def mock_tiered_cache():
    """提供模拟多级缓存实例"""
    from app.core.tiered_cache import TieredCacheManager
    cache = TieredCacheManager(l1_size=100, l1_ttl=60, l2_ttl=300)
    yield cache
    cache.clear()


@pytest.fixture(scope="function")
def mock_circuit_breaker():
    """提供模拟熔断器实例"""
    from app.core.circuit_breaker import CircuitBreaker

    breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=10,
        half_open_max_calls=2
    )
    yield breaker


@pytest.fixture(scope="function")
def mock_school_data():
    """提供模拟学校数据"""
    return {
        "schools": [
            {
                "id": 1,
                "name": "昆明市第一中学",
                "city": "昆明市",
                "district": "五华区",
                "level": "一级一等",
                "type": "公办"
            },
            {
                "id": 2,
                "name": "云南师范大学附属中学",
                "city": "昆明市",
                "district": "五华区",
                "level": "一级一等",
                "type": "公办"
            }
        ]
    }


@pytest.fixture(scope="function")
def mock_user_data():
    """提供模拟用户数据"""
    return {
        "user_id": "test_user_001",
        "username": "test_user",
        "phone": "13800138000",
        "region": "昆明市",
        "score": 580
    }


@pytest.fixture(scope="function")
def mock_policy_data():
    """提供模拟政策数据"""
    return {
        "policies": [
            {
                "id": 1,
                "title": "2026年昆明市中考招生政策",
                "city": "昆明市",
                "year": 2026,
                "content": "昆明市2026年中考招生政策详细说明..."
            }
        ]
    }


@pytest.fixture(scope="function")
def temp_db(tmp_path):
    """提供临时数据库路径"""
    db_path = tmp_path / "test.db"
    yield str(db_path)
    if db_path.exists():
        db_path.unlink()


def pytest_configure(config):
    """pytest配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集项"""
    for item in items:
        # 自动为所有测试添加unit标记
        if "unit" not in item.keywords:
            item.add_marker(pytest.mark.unit)
