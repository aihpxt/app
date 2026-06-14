"""
JWT Token处理模块
提供JWT Token的生成、验证和刷新功能
"""

import os
import jwt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from fastapi import HTTPException, Request, status
import logging

logger = logging.getLogger(__name__)


class JWTConfig:
    """JWT配置类"""
    # 从环境变量读取配置，如果未设置则使用默认值
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    TOKEN_TYPE = "Bearer"


class JWTHandler:
    """JWT Token处理器"""

    def __init__(self, config: JWTConfig = None):
        self.config = config or JWTConfig()

    def create_access_token(
        self,
        user_id: str,
        username: str,
        roles: list = None,
        additional_data: Dict[str, Any] = None
    ) -> str:
        """
        创建访问令牌

        Args:
            user_id: 用户ID
            username: 用户名
            roles: 用户角色列表
            additional_data: 附加数据

        Returns:
            JWT Token字符串
        """
        expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": user_id,
            "username": username,
            "roles": roles or [],
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": expire,
            "jti": self._generate_jti()
        }

        if additional_data:
            payload.update(additional_data)

        token = jwt.encode(
            payload,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )

        logger.info(f"Created access token for user: {username}")
        return token

    def create_refresh_token(self, user_id: str) -> str:
        """
        创建刷新令牌

        Args:
            user_id: 用户ID

        Returns:
            JWT Refresh Token字符串
        """
        expire = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": expire,
            "jti": self._generate_jti()
        }

        token = jwt.encode(
            payload,
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )

        logger.info(f"Created refresh token for user_id: {user_id}")
        return token

    def create_token_pair(
        self,
        user_id: str,
        username: str,
        roles: list = None,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        创建令牌对（访问令牌+刷新令牌）

        Returns:
            包含access_token和refresh_token的字典
        """
        access_token = self.create_access_token(
            user_id=user_id,
            username=username,
            roles=roles,
            additional_data=additional_data
        )
        refresh_token = self.create_refresh_token(user_id=user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": self.config.TOKEN_TYPE,
            "expires_in": self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def verify_token(self, token: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        验证JWT Token

        Args:
            token: JWT Token字符串

        Returns:
            (是否成功, payload数据, 错误信息)
        """
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )
            return True, payload, None

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return False, {}, "Token has expired"

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return False, {}, "Invalid token"

    def verify_access_token(self, token: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        验证访问令牌

        Args:
            token: JWT Token字符串

        Returns:
            (是否成功, payload数据, 错误信息)
        """
        success, payload, error = self.verify_token(token)

        if not success:
            return success, payload, error

        if payload.get("type") != "access":
            return False, {}, "Invalid token type"

        return success, payload, error

    def verify_refresh_token(self, token: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        验证刷新令牌

        Args:
            token: JWT Token字符串

        Returns:
            (是否成功, payload数据, 错误信息)
        """
        success, payload, error = self.verify_token(token)

        if not success:
            return success, payload, error

        if payload.get("type") != "refresh":
            return False, {}, "Invalid token type"

        return success, payload, error

    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        使用刷新令牌获取新的访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            (是否成功, 新令牌数据, 错误信息)
        """
        success, payload, error = self.verify_refresh_token(refresh_token)

        if not success:
            return success, {}, error

        user_id = payload.get("sub")
        if not user_id:
            return False, {}, "Invalid token payload"

        # 注意：实际应用中应该从数据库获取用户信息和角色
        # 这里简化处理，直接使用token中的信息
        new_access_token = self.create_access_token(
            user_id=user_id,
            username=payload.get("username", ""),
            roles=payload.get("roles", [])
        )

        return True, {
            "access_token": new_access_token,
            "token_type": self.config.TOKEN_TYPE,
            "expires_in": self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }, None

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        解码Token（不验证）

        Args:
            token: JWT Token字符串

        Returns:
            解码后的payload数据
        """
        try:
            return jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
                options={"verify_exp": False}
            )
        except Exception:
            return None

    def _generate_jti(self) -> str:
        """生成JWT ID"""
        import secrets
        return secrets.token_urlsafe(16)


# 全局JWT处理器实例
_jwt_handler = None


def get_jwt_handler() -> JWTHandler:
    """获取JWT处理器实例"""
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler()
    return _jwt_handler


def require_auth(func):
    """
    认证装饰器
    验证请求中的JWT Token
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 从kwargs获取request
        request = kwargs.get('request')
        if not request:
            # 尝试从args获取
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="无法获取请求对象"
            )

        # 从Authorization header获取token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 验证Bearer token格式
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证格式",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = parts[1]

        # 验证token
        jwt_handler = get_jwt_handler()
        success, payload, error = jwt_handler.verify_access_token(token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error,
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 将用户信息添加到request state
        request.state.user = payload
        request.state.user_id = payload.get("sub")
        request.state.username = payload.get("username")
        request.state.roles = payload.get("roles", [])

        return await func(*args, **kwargs)

    return wrapper


def require_role(*required_roles):
    """
    角色要求装饰器
    必须在require_auth之后使用

    Args:
        required_roles: 必需的角色列表
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs获取request
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="无法获取请求对象"
                )

            # 检查用户角色
            user_roles = getattr(request.state, 'roles', [])
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator
