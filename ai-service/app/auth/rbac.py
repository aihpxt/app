"""
RBAC权限管理模块
实现基于角色的访问控制（Role-Based Access Control）
"""

from enum import Enum
from typing import List, Set, Optional, Dict, Any
from functools import wraps
from fastapi import HTTPException, Request, status
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """系统角色枚举"""
    ADMIN = "admin"           # 管理员
    TEACHER = "teacher"       # 教师
    STUDENT = "student"        # 学生
    GUEST = "guest"           # 访客


class Permission(str, Enum):
    """系统权限枚举"""
    # 用户管理权限
    USER_VIEW = "user:view"           # 查看用户
    USER_CREATE = "user:create"         # 创建用户
    USER_UPDATE = "user:update"         # 更新用户
    USER_DELETE = "user:delete"         # 删除用户

    # 学校管理权限
    SCHOOL_VIEW = "school:view"         # 查看学校
    SCHOOL_CREATE = "school:create"     # 创建学校
    SCHOOL_UPDATE = "school:update"     # 更新学校
    SCHOOL_DELETE = "school:delete"     # 删除学校

    # 政策管理权限
    POLICY_VIEW = "policy:view"         # 查看政策
    POLICY_CREATE = "policy:create"     # 创建政策
    POLICY_UPDATE = "policy:update"     # 更新政策
    POLICY_DELETE = "policy:delete"     # 删除政策

    # AI功能权限
    AI_QUERY = "ai:query"             # AI查询
    AI_RECOMMEND = "ai:recommend"      # AI推荐
    AI_PREDICT = "ai:predict"          # AI预测

    # 系统管理权限
    SYSTEM_CONFIG = "system:config"     # 系统配置
    SYSTEM_LOG = "system:log"          # 系统日志
    SYSTEM_MONITOR = "system:monitor"  # 系统监控


# 角色权限映射
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # 管理员拥有所有权限
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.SCHOOL_VIEW,
        Permission.SCHOOL_CREATE,
        Permission.SCHOOL_UPDATE,
        Permission.SCHOOL_DELETE,
        Permission.POLICY_VIEW,
        Permission.POLICY_CREATE,
        Permission.POLICY_UPDATE,
        Permission.POLICY_DELETE,
        Permission.AI_QUERY,
        Permission.AI_RECOMMEND,
        Permission.AI_PREDICT,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_LOG,
        Permission.SYSTEM_MONITOR,
    },
    Role.TEACHER: {
        # 教师权限
        Permission.USER_VIEW,
        Permission.SCHOOL_VIEW,
        Permission.SCHOOL_UPDATE,
        Permission.POLICY_VIEW,
        Permission.AI_QUERY,
        Permission.AI_RECOMMEND,
        Permission.AI_PREDICT,
        Permission.SYSTEM_LOG,
    },
    Role.STUDENT: {
        # 学生权限
        Permission.SCHOOL_VIEW,
        Permission.POLICY_VIEW,
        Permission.AI_QUERY,
        Permission.AI_RECOMMEND,
        Permission.AI_PREDICT,
    },
    Role.GUEST: {
        # 访客权限
        Permission.SCHOOL_VIEW,
        Permission.POLICY_VIEW,
    },
}


class RBACManager:
    """RBAC权限管理器"""

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def get_role_permissions(self, role: Role) -> Set[Permission]:
        """
        获取角色的权限集合

        Args:
            role: 角色

        Returns:
            权限集合
        """
        return self.role_permissions.get(role, set())

    def get_user_permissions(self, roles: List[str]) -> Set[Permission]:
        """
        获取用户的综合权限集合

        Args:
            roles: 用户角色列表

        Returns:
            综合权限集合
        """
        permissions = set()
        for role_str in roles:
            try:
                role = Role(role_str)
                permissions.update(self.get_role_permissions(role))
            except ValueError:
                logger.warning(f"Unknown role: {role_str}")

        return permissions

    def has_permission(self, roles: List[str], permission: Permission) -> bool:
        """
        检查用户是否具有指定权限

        Args:
            roles: 用户角色列表
            permission: 权限

        Returns:
            是否具有权限
        """
        user_permissions = self.get_user_permissions(roles)
        return permission in user_permissions

    def has_any_permission(self, roles: List[str], permissions: List[Permission]) -> bool:
        """
        检查用户是否具有指定权限列表中的任意一个

        Args:
            roles: 用户角色列表
            permissions: 权限列表

        Returns:
            是否具有任意一个权限
        """
        user_permissions = self.get_user_permissions(roles)
        return any(p in user_permissions for p in permissions)

    def has_all_permissions(self, roles: List[str], permissions: List[Permission]) -> bool:
        """
        检查用户是否具有所有指定权限

        Args:
            roles: 用户角色列表
            permissions: 权限列表

        Returns:
            是否具有所有权限
        """
        user_permissions = self.get_user_permissions(roles)
        return all(p in user_permissions for p in permissions)

    def is_admin(self, roles: List[str]) -> bool:
        """
        检查用户是否为管理员

        Args:
            roles: 用户角色列表

        Returns:
            是否为管理员
        """
        return Role.ADMIN.value in roles

    def is_teacher(self, roles: List[str]) -> bool:
        """
        检查用户是否为教师

        Args:
            roles: 用户角色列表

        Returns:
            是否为教师
        """
        return Role.TEACHER.value in roles

    def is_student(self, roles: List[str]) -> bool:
        """
        检查用户是否为学生

        Args:
            roles: 用户角色列表

        Returns:
            是否为学生
        """
        return Role.STUDENT.value in roles


# 全局RBAC管理器实例
_rbac_manager = None


def get_rbac_manager() -> RBACManager:
    """获取RBAC管理器实例"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager


def require_permission(*required_permissions):
    """
    权限要求装饰器
    必须在require_auth之后使用

    Args:
        required_permissions: 必需的权限列表
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

            # 获取用户角色
            user_roles = getattr(request.state, 'roles', [])
            if not user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户未分配角色"
                )

            # 检查权限
            rbac_manager = get_rbac_manager()
            if not rbac_manager.has_any_permission(user_roles, list(required_permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def check_permission(roles: List[str], permission: Permission) -> bool:
    """
    便捷的权限检查函数

    Args:
        roles: 用户角色列表
        permission: 权限

    Returns:
        是否具有权限
    """
    rbac_manager = get_rbac_manager()
    return rbac_manager.has_permission(roles, permission)


class UserContext:
    """用户上下文"""

    def __init__(self, user_id: str, username: str, roles: List[str]):
        self.user_id = user_id
        self.username = username
        self.roles = roles
        self.rbac_manager = get_rbac_manager()

    @property
    def permissions(self) -> Set[Permission]:
        """获取用户权限"""
        return self.rbac_manager.get_user_permissions(self.roles)

    def has_permission(self, permission: Permission) -> bool:
        """检查权限"""
        return permission in self.permissions

    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.rbac_manager.is_admin(self.roles)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "roles": self.roles,
            "permissions": [p.value for p in self.permissions]
        }


def get_user_context(request: Request) -> Optional[UserContext]:
    """
    从请求中获取用户上下文

    Args:
        request: FastAPI请求对象

    Returns:
        用户上下文对象
    """
    if not hasattr(request.state, 'user_id'):
        return None

    return UserContext(
        user_id=request.state.user_id,
        username=getattr(request.state, 'username', ''),
        roles=getattr(request.state, 'roles', [])
    )


async def get_current_user_context(request: Request) -> UserContext:
    """
    FastAPI依赖注入：获取当前用户上下文
    
    从Authorization header中提取并验证JWT token
    返回UserContext对象，如果验证失败则抛出HTTPException
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        用户上下文对象
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    from app.auth.jwt_handler import get_jwt_handler
    
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

    # 提取用户信息
    user_id = payload.get("sub")
    username = payload.get("username", "")
    roles = payload.get("roles", [])

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 设置request.state以便后续使用
    request.state.user_id = user_id
    request.state.username = username
    request.state.roles = roles

    return UserContext(
        user_id=user_id,
        username=username,
        roles=roles
    )
