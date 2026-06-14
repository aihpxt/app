"""
认证API路由
提供登录、登出、Token刷新等认证功能
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import logging

from app.auth.jwt_handler import get_jwt_handler, require_auth
from app.auth.rbac import Role, get_user_context, get_current_user_context, UserContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """刷新Token响应"""
    access_token: str
    token_type: str
    expires_in: int


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str = "student"


class UserInfo(BaseModel):
    """用户信息"""
    user_id: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    roles: List[str]
    created_at: Optional[str] = None


@router.post("/login")
async def login(request: LoginRequest):
    """
    用户登录

    - **username**: 用户名或手机号
    - **password**: 密码

    返回访问令牌和刷新令牌
    """
    try:
        jwt_handler = get_jwt_handler()

        user = await verify_credentials(request.username, request.password)

        if not user:
            return {
                "success": False,
                "message": "用户名或密码错误"
            }

        # 生成Token对
        tokens = jwt_handler.create_token_pair(
            user_id=user["user_id"],
            username=user["username"],
            roles=user["roles"],
            additional_data={"email": user.get("email")}
        )

        logger.info(f"User {user['username']} logged in successfully")

        return {
            "success": True,
            "data": {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": tokens["token_type"],
                "expires_in": tokens["expires_in"],
                "user": {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "phone": user.get("phone"),
                    "email": user.get("email"),
                    "roles": user["roles"]
                }
            }
        }

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return {
            "success": False,
            "message": "登录失败，请稍后重试"
        }


@router.post("/logout")
async def logout(request: Request):
    """
    用户登出

    清除用户会话
    """
    try:
        user_context = get_user_context(request)

        if user_context:
            logger.info(f"User {user_context.username} logged out")
        else:
            logger.info("Anonymous user logged out")

        return {"message": "登出成功"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    刷新访问令牌

    使用刷新令牌获取新的访问令牌
    """
    try:
        jwt_handler = get_jwt_handler()

        success, result, error = jwt_handler.refresh_access_token(request.refresh_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error
            )

        return RefreshTokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token刷新失败"
        )


@router.get("/me", response_model=UserInfo)
async def get_current_user(user_context: UserContext = Depends(get_current_user_context)):
    """
    获取当前用户信息
    
    需要有效的JWT Token
    """
    try:
        return UserInfo(
            user_id=user_context.user_id,
            username=user_context.username,
            roles=user_context.roles,
            email=None,
            phone=None
        )
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")


@router.post("/register")
async def register(request: RegisterRequest):
    """
    用户注册

    创建新用户账号
    """
    try:
        if len(request.password) < 6:
            return {
                "success": False,
                "message": "密码长度至少6位"
            }

        # 验证角色
        valid_roles = [r.value for r in Role]
        if request.role not in valid_roles:
            request.role = "student"

        import bcrypt
        from app.core.database_pool import get_db_manager
        from app.models.user import User

        # 检查用户名和手机号是否已存在
        db_manager = get_db_manager()
        session = db_manager.get_session()
        try:
            existing = session.query(User).filter(
                (User.username == request.username) | (User.phone == request.phone)
            ).first()
            if existing:
                if existing.username == request.username:
                    return {
                        "success": False,
                        "message": "用户名已存在"
                    }
                else:
                    return {
                        "success": False,
                        "message": "手机号已注册"
                    }

            # 密码哈希
            password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 创建用户
            new_user = User(
                username=request.username,
                password_hash=password_hash,
                email=request.email,
                phone=request.phone,
                role=request.role
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            logger.info(f"New user registered: {request.username} (id={new_user.id})")

            return {
                "success": True,
                "data": {
                    "user_id": str(new_user.id),
                    "username": new_user.username,
                    "email": new_user.email,
                    "phone": new_user.phone,
                    "roles": [new_user.role],
                    "created_at": new_user.created_at.isoformat() if new_user.created_at else datetime.now().isoformat()
                },
                "message": "注册成功"
            }
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Register error: {type(e).__name__}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"注册失败: {str(e)}"
        }


# 辅助函数：验证用户凭据
async def verify_credentials(username: str, password: str) -> Optional[dict]:
    """
    验证用户凭据
    支持用户名或手机号登录

    Args:
        username: 用户名或手机号
        password: 密码

    Returns:
        用户信息字典，验证失败返回None
    """
    import bcrypt
    from app.core.database_pool import get_db_manager
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        from app.models.user import User
        user = session.query(User).filter(
            (User.username == username) | (User.phone == username)
        ).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {
                "user_id": str(user.id),
                "username": user.username,
                "phone": user.phone,
                "email": user.email,
                "roles": [user.role]
            }
        return None
    finally:
        session.close()
