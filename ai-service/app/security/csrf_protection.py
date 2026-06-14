"""
CSRF防护模块
提供CSRF Token机制和中间件
"""

import secrets
import hashlib
import time
from typing import Optional, Dict, Callable
from functools import wraps
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class CSRFTokenManager:
    """CSRF Token管理器"""

    def __init__(self, token_ttl: int = 3600):
        """
        初始化CSRF Token管理器

        Args:
            token_ttl: Token有效期（秒）
        """
        self.token_ttl = token_ttl
        self._tokens: Dict[str, Dict] = {}

    def generate_token(self, session_id: str) -> str:
        """
        生成CSRF Token

        Args:
            session_id: 会话ID

        Returns:
            CSRF Token
        """
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)

        self._tokens[session_id] = {
            'token_hash': token_hash,
            'created_at': time.time()
        }

        return token

    def verify_token(self, session_id: str, token: str) -> bool:
        """
        验证CSRF Token

        Args:
            session_id: 会话ID
            token: 待验证的Token

        Returns:
            是否验证通过
        """
        if not session_id or not token:
            return False

        token_data = self._tokens.get(session_id)
        if not token_data:
            return False

        # 检查Token是否过期
        if time.time() - token_data['created_at'] > self.token_ttl:
            del self._tokens[session_id]
            return False

        # 验证Token
        token_hash = self._hash_token(token)
        return token_hash == token_data['token_hash']

    def remove_token(self, session_id: str) -> None:
        """
        移除CSRF Token

        Args:
            session_id: 会话ID
        """
        if session_id in self._tokens:
            del self._tokens[session_id]

    def _hash_token(self, token: str) -> str:
        """对Token进行哈希"""
        return hashlib.sha256(token.encode()).hexdigest()


# 全局CSRF Token管理器实例
_csrf_manager = None


def get_csrf_manager() -> CSRFTokenManager:
    """获取CSRF Token管理器实例"""
    global _csrf_manager
    if _csrf_manager is None:
        _csrf_manager = CSRFTokenManager()
    return _csrf_manager


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF中间件"""

    def __init__(self, app, exclude_paths: list = None):
        """
        初始化CSRF中间件

        Args:
            app: FastAPI应用
            exclude_paths: 排除检查的路径列表
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/refresh',
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json'
        ]

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 检查是否需要CSRF检查
        if self._should_check(request):
            # 获取Session ID（从请求头或Cookie）
            session_id = self._get_session_id(request)

            if session_id:
                # 获取请求中的CSRF Token
                csrf_token = await self._get_csrf_token(request)

                if csrf_token:
                    # 验证Token
                    csrf_manager = get_csrf_manager()
                    if not csrf_manager.verify_token(session_id, csrf_token):
                        logger.warning(f"CSRF token verification failed for session: {session_id}")
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="CSRF token verification failed"
                        )

        response = await call_next(request)
        return response

    def _should_check(self, request: Request) -> bool:
        """检查是否需要CSRF检查"""
        # 只对POST、PUT、DELETE等修改性请求进行检查
        if request.method not in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return False

        # 检查是否在排除列表中
        path = request.url.path
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return False

        return True

    def _get_session_id(self, request: Request) -> Optional[str]:
        """获取Session ID"""
        # 从请求头获取
        session_id = request.headers.get('X-Session-ID')
        if session_id:
            return session_id

        # 从Cookie获取
        session_id = request.cookies.get('session_id')
        if session_id:
            return session_id

        return None

    async def _get_csrf_token(self, request: Request) -> Optional[str]:
        """获取CSRF Token"""
        # 从请求头获取（推荐方式）
        csrf_token = request.headers.get('X-CSRF-Token')
        if csrf_token:
            return csrf_token

        # 从表单数据获取
        try:
            form = await request.form()
            csrf_token = form.get('csrf_token')
            if csrf_token:
                return csrf_token
        except Exception:
            pass

        return None


def csrf_protect(func: Callable):
    """
    CSRF保护装饰器

    用于需要CSRF保护的具体端点
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None

        # 尝试获取request对象
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if not request:
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                    break

        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="无法获取请求对象"
            )

        # 获取Session ID
        session_id = None
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            session_id = request.cookies.get('session_id')

        # 获取CSRF Token
        csrf_token = request.headers.get('X-CSRF-Token')

        if session_id and csrf_token:
            csrf_manager = get_csrf_manager()
            if not csrf_manager.verify_token(session_id, csrf_token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token verification failed"
                )

        return await func(*args, **kwargs)

    return wrapper


def generate_csrf_token(session_id: str) -> str:
    """
    生成CSRF Token的便捷函数

    Args:
        session_id: 会话ID

    Returns:
        CSRF Token
    """
    csrf_manager = get_csrf_manager()
    return csrf_manager.generate_token(session_id)
