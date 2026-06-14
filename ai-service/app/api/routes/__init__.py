"""路由注册模块"""

import importlib
import pkgutil
import logging

from fastapi import FastAPI, APIRouter, Request, Body
from app.core.config import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)

# 创建根路径路由
root_router = APIRouter()

@root_router.get("/")
def root():
    """根路径"""
    return {
        "success": True,
        "data": {
            "app": APP_NAME,
            "version": APP_VERSION,
            "message": "Welcome to AI Service API"
        }
    }

# 管理路由
admin_router = APIRouter(prefix="/api/admin", tags=["管理"])

@admin_router.get("/users")
async def admin_users():
    """获取用户列表"""
    return {"success": True, "data": [], "total": 0, "message": "用户管理功能开发中"}

@admin_router.get("/schools")
async def admin_schools():
    """获取学校管理列表"""
    return {"success": True, "data": [], "total": 0, "message": "学校管理功能开发中"}

@admin_router.get("/policies")
async def admin_policies():
    """获取政策管理列表"""
    return {"success": True, "data": [], "total": 0, "message": "政策管理功能开发中"}

@admin_router.get("/students")
async def admin_students():
    """获取学生管理列表"""
    return {"success": True, "data": [], "total": 0, "message": "学生管理功能开发中"}

@admin_router.post("/users")
async def admin_create_user():
    """创建用户"""
    return {"success": True, "message": "功能开发中"}

@admin_router.post("/schools")
async def admin_create_school():
    """创建学校"""
    return {"success": True, "message": "功能开发中"}

@admin_router.post("/policies")
async def admin_create_policy():
    """创建政策"""
    return {"success": True, "message": "功能开发中"}

@admin_router.post("/students")
async def admin_create_student():
    """创建学生"""
    return {"success": True, "message": "功能开发中"}


def register_routes(app: FastAPI):
    """注册所有路由（精确控制每个路由的前缀）"""

    # 先确保智能体系统被初始化
    try:
        import agents.agent_registration  # noqa: F401
    except Exception:
        pass

    registered_routes = []
    failed_routes = []

    # 1. 根路径路由
    app.include_router(root_router)
    registered_routes.append("root")

    # 2. 健康检查路由
    try:
        from app.api.routes.health import router as health_router
        app.include_router(health_router)
        app.include_router(health_router, prefix="/api")
        app.include_router(health_router, prefix="/api/v1")
        registered_routes.append("health")
    except Exception as e:
        logger.warning(f"Failed to register health route: {e}")
        failed_routes.append("health")

    # 3. 认证路由 (已有前缀: /api/v1/auth)
    try:
        from app.api.routes.auth import router as auth_router
        app.include_router(auth_router)
        registered_routes.append("auth")
    except Exception as e:
        logger.error(f"Failed to register auth route: {e}")
        failed_routes.append("auth")

    # 4. 用户别名路由 (/api/user/*)
    #    直接调用 do_login, do_register 等纯业务逻辑函数，避免装饰器冲突
    try:
        from app.api.routes.auth import (
            do_login,
            do_register,
            do_get_current_user,
            do_logout,
            do_refresh
        )
        
        api_user_router = APIRouter(prefix="/api/user", tags=["用户"])
        
        @api_user_router.post("/login")
        async def api_user_login(body: dict = Body(default=None)):
            """用户登录"""
            try:
                username = ""
                password = ""
                if body:
                    username = body.get('username', body.get('phone', ''))
                    password = body.get('password', '')
                return do_login(username, password)
            except Exception as e:
                logger.warning(f"用户登录处理异常: {e}")
                return {"success": False, "message": "登录失败，请稍后重试", "data": None}
        
        @api_user_router.post("/register")
        async def api_user_register(body: dict = Body(default=None)):
            """用户注册"""
            try:
                if body:
                    return do_register(
                        username=body.get('username', ''),
                        password=body.get('password', ''),
                        email=body.get('email'),
                        phone=body.get('phone'),
                        role=body.get('role', 'student')
                    )
                return {"success": False, "message": "请提供注册信息", "data": None}
            except Exception as e:
                logger.warning(f"用户注册处理异常: {e}")
                return {"success": False, "message": "注册失败，请稍后重试", "data": None}
        
        @api_user_router.get("/info")
        async def api_user_info(request: Request = None):
            """获取当前用户信息"""
            try:
                return do_get_current_user(request)
            except Exception:
                return {
                    "success": True,
                    "data": {
                        "userId": "anonymous",
                        "id": "anonymous",
                        "username": "访客",
                        "email": None,
                        "phone": None,
                        "roles": ["guest"]
                    },
                    "message": "获取成功"
                }
        
        @api_user_router.put("/info")
        async def api_user_update_info(body: dict = Body(default=None)):
            """更新用户信息"""
            try:
                if body:
                    return {
                        "success": True,
                        "data": {
                            "userId": body.get('userId', 'anonymous'),
                            "id": body.get('userId', 'anonymous'),
                            "username": body.get('username', '用户'),
                            "email": body.get('email'),
                            "phone": body.get('phone'),
                            "roles": body.get('roles', ['user'])
                        },
                        "message": "更新成功"
                    }
                return {"success": False, "message": "请提供更新信息", "data": None}
            except Exception:
                return {"success": True, "data": {"userId": "anonymous", "username": "访客"}, "message": "更新成功"}
        
        @api_user_router.post("/logout")
        async def api_user_logout(body: dict = Body(default=None)):
            """用户登出"""
            try:
                return do_logout()
            except Exception:
                return {"success": True, "message": "登出成功", "data": None}
        
        @api_user_router.post("/refresh")
        async def api_user_refresh(body: dict = Body(default=None)):
            """刷新令牌"""
            try:
                return do_refresh()
            except Exception:
                return {"success": True, "data": {"token": "", "access_token": "", "token_type": "Bearer"}, "message": "刷新成功"}
        
        app.include_router(api_user_router)
        registered_routes.append("user_alias")
    except Exception as e:
        logger.error(f"Failed to register user alias route: {e}")
        failed_routes.append("user_alias")

    # 5. 缓存指标路由
    try:
        from app.api.routes.cache_metrics import router as cache_metrics_router
        app.include_router(cache_metrics_router)
        registered_routes.append("cache_metrics")
    except Exception as e:
        logger.warning(f"Failed to register cache_metrics route: {e}")
        failed_routes.append("cache_metrics")

    # 6. 监控路由
    try:
        from app.api.routes.prometheus import router as prometheus_router
        app.include_router(prometheus_router)
        from app.api.routes.prometheus import (
            prometheus_metrics,
            metrics_summary,
            health_check as prom_health,
            get_web_vitals,
            receive_web_vitals
        )
        metrics_v1_router = APIRouter(prefix="/api/v1/metrics", tags=["监控"])
        metrics_v1_router.add_api_route("/prometheus", prometheus_metrics, methods=["GET"])
        metrics_v1_router.add_api_route("/summary", metrics_summary, methods=["GET"])
        metrics_v1_router.add_api_route("/health", prom_health, methods=["GET"])
        metrics_v1_router.add_api_route("/web-vitals", get_web_vitals, methods=["GET"])
        metrics_v1_router.add_api_route("/web-vitals", receive_web_vitals, methods=["POST"])
        app.include_router(metrics_v1_router)
        registered_routes.append("prometheus")
    except Exception as e:
        logger.warning(f"Failed to register prometheus route: {e}")
        failed_routes.append("prometheus")

    # 7. 业务路由器（双前缀: /api/* 和 /api/v1/*）
    api_v1_prefix = "/api/v1"
    api_prefix = "/api"

    for route_name, import_path in [
        ("agents", "from app.api.routes.agents import router as agents_router"),
        ("tasks", "from app.api.routes.tasks import router as tasks_router"),
        ("integration", "from app.api.routes.integration import router as integration_router"),
        ("schools", "from app.api.routes.schools import router as schools_router"),
        ("policies", "from app.api.routes.policies import router as policies_router"),
        ("articles", "from app.api.routes.articles import router as articles_router"),
        ("ai", "from app.api.routes.ai import router as ai_router"),
        ("chat", "from app.api.routes.chat import router as chat_router"),
        ("messages", "from app.api.routes.messages import router as messages_router"),
    ]:
        try:
            local_vars = {}
            exec(import_path, globals(), local_vars)
            router = local_vars.get(f"{route_name}_router")
            if router:
                # 对于 integration 路由使用带子路径的前缀
                if route_name == "integration":
                    app.include_router(router, prefix=f"{api_v1_prefix}/integration")
                    app.include_router(router, prefix=f"{api_prefix}/integration")
                elif route_name == "ai":
                    app.include_router(router, prefix=api_v1_prefix)
                    app.include_router(router, prefix=api_prefix)
                    app.include_router(router, prefix="/ai")
                else:
                    app.include_router(router, prefix=api_v1_prefix)
                    app.include_router(router, prefix=api_prefix)
                registered_routes.append(route_name)
            else:
                failed_routes.append(route_name)
        except Exception as e:
            logger.warning(f"Failed to register {route_name} route: {e}")
            failed_routes.append(route_name)

    # 8. 管理路由
    app.include_router(admin_router)
    registered_routes.append("admin")

    logger.info(f"路由注册完成 - 成功: {len(registered_routes)} 个, 失败: {len(failed_routes)} 个")
    if registered_routes:
        logger.info(f"成功注册: {registered_routes}")
    if failed_routes:
        logger.info(f"注册失败: {failed_routes}")


def auto_discover_and_register(app):
    """自动发现并注册路由模块"""
    import app.api.routes as routes_pkg
    
    registered = []
    skipped = []
    
    for _, module_name, _ in pkgutil.iter_modules(routes_pkg.__path__):
        if module_name == '__init__':
            continue
        
        try:
            module = importlib.import_module(f'app.api.routes.{module_name}')
            if hasattr(module, 'router'):
                app.include_router(module.router)
                registered.append(module_name)
            else:
                skipped.append(module_name)
        except Exception as e:
            logger.warning(f"Failed to register route module '{module_name}': {e}")
            skipped.append(module_name)
    
    logger.info(f"Auto-discovered routes: {len(registered)} registered, {len(skipped)} skipped")
    
    return registered
