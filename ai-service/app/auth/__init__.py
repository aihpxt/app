"""
认证授权模块
提供JWT Token和RBAC权限管理功能
"""

from app.auth.jwt_handler import (
    JWTConfig,
    JWTHandler,
    get_jwt_handler,
    require_auth,
    require_role,
)
from app.auth.rbac import (
    Role,
    Permission,
    RBACManager,
    get_rbac_manager,
    require_permission,
    check_permission,
    UserContext,
    get_user_context,
)

__all__ = [
    # JWT
    "JWTConfig",
    "JWTHandler",
    "get_jwt_handler",
    "require_auth",
    "require_role",
    # RBAC
    "Role",
    "Permission",
    "RBACManager",
    "get_rbac_manager",
    "require_permission",
    "check_permission",
    "UserContext",
    "get_user_context",
]
