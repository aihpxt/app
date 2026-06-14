"""路由注册模块"""

import importlib
import pkgutil
import logging

from fastapi import FastAPI, APIRouter
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

# 创建用户路由别名（映射 /api/user/* 到 /api/v1/auth/* 的处理逻辑）
user_router = APIRouter(prefix="/api/user", tags=["用户"])

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
    """注册所有路由（精确控制每个路由的前缀）
    
    使用 try-except 包裹每个模块导入，确保单个路由模块失败不会阻塞整个应用启动
    """

    registered_routes = []
    failed_routes = []

    # =====================================================
    # 1. 根路径路由
    # =====================================================
    app.include_router(root_router)
    registered_routes.append("root")

    # =====================================================
    # 2. 健康检查路由（无前缀路由器）
    #    支持: /health, /api/health, /api/v1/health
    # =====================================================
    try:
        from app.api.routes.health import router as health_router
        app.include_router(health_router)
        app.include_router(health_router, prefix="/api")
        app.include_router(health_router, prefix="/api/v1")
        registered_routes.append("health")
    except Exception as e:
        logger.warning(f"Failed to register health route: {e}")
        failed_routes.append("health")

    # =====================================================
    # 3. 认证路由（已有内部前缀: /api/v1/auth）
    #    支持: /api/v1/auth/*
    # =====================================================
    try:
        from app.api.routes.auth import router as auth_router
        app.include_router(auth_router)
        registered_routes.append("auth")
    except Exception as e:
        logger.error(f"Failed to register auth route: {e}")
        failed_routes.append("auth")

    # =====================================================
    # 4. 用户别名路由（用户友好路径）
    #    将 auth 模块的端点重新挂载到 /api/user/* 下
    #    支持: /api/user/login, /api/user/register, 等
    # =====================================================
    try:
        from app.api.routes.auth import login, register, get_current_user, logout, refresh_token
        user_router.add_api_route("/login", login, methods=["POST"])
        user_router.add_api_route("/register", register, methods=["POST"])
        user_router.add_api_route("/info", get_current_user, methods=["GET"])
        user_router.add_api_route("/logout", logout, methods=["POST"])
        user_router.add_api_route("/refresh", refresh_token, methods=["POST"])
        app.include_router(user_router)
        registered_routes.append("user_alias")
    except Exception as e:
        logger.error(f"Failed to register user alias route: {e}")
        failed_routes.append("user_alias")

    # =====================================================
    # 5. 缓存指标路由（已有内部前缀: /api/v1/cache）
    #    支持: /api/v1/cache/*
    # =====================================================
    try:
        from app.api.routes.cache_metrics import router as cache_metrics_router
        app.include_router(cache_metrics_router)
        registered_routes.append("cache_metrics")
    except Exception as e:
        logger.warning(f"Failed to register cache_metrics route: {e}")
        failed_routes.append("cache_metrics")

    # =====================================================
    # 6. 监控路由（已有内部前缀: /api/metrics）
    #    同时额外添加 /api/v1/metrics 作为别名
    #    支持: /api/metrics/* 和 /api/v1/metrics/*
    # =====================================================
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

    # =====================================================
    # 7. 无前缀的业务路由器（需要在 include 时指定前缀）
    #    双前缀支持: /api/* 和 /api/v1/*
    # =====================================================
    api_v1_prefix = "/api/v1"
    api_prefix = "/api"

    # agents_router - 可能会有复杂依赖，单独处理
    try:
        from app.api.routes.agents import router as agents_router
        app.include_router(agents_router, prefix=api_v1_prefix)
        app.include_router(agents_router, prefix=api_prefix)
        registered_routes.append("agents")
    except Exception as e:
        logger.warning(f"Failed to register agents route: {e}")
        failed_routes.append("agents")

    try:
        from app.api.routes.tasks import router as tasks_router
        app.include_router(tasks_router, prefix=api_v1_prefix)
        app.include_router(tasks_router, prefix=api_prefix)
        registered_routes.append("tasks")
    except Exception as e:
        logger.warning(f"Failed to register tasks route: {e}")
        failed_routes.append("tasks")

    try:
        from app.api.routes.integration import router as integration_router
        app.include_router(integration_router, prefix=f"{api_v1_prefix}/integration")
        app.include_router(integration_router, prefix=f"{api_prefix}/integration")
        registered_routes.append("integration")
    except Exception as e:
        logger.warning(f"Failed to register integration route: {e}")
        failed_routes.append("integration")

    try:
        from app.api.routes.schools import router as schools_router
        app.include_router(schools_router, prefix=api_v1_prefix)
        app.include_router(schools_router, prefix=api_prefix)
        registered_routes.append("schools")
    except Exception as e:
        logger.warning(f"Failed to register schools route: {e}")
        failed_routes.append("schools")

    try:
        from app.api.routes.policies import router as policies_router
        app.include_router(policies_router, prefix=api_v1_prefix)
        app.include_router(policies_router, prefix=api_prefix)
        registered_routes.append("policies")
    except Exception as e:
        logger.warning(f"Failed to register policies route: {e}")
        failed_routes.append("policies")

    try:
        from app.api.routes.articles import router as articles_router
        app.include_router(articles_router, prefix=api_v1_prefix)
        app.include_router(articles_router, prefix=api_prefix)
        registered_routes.append("articles")
    except Exception as e:
        logger.warning(f"Failed to register articles route: {e}")
        failed_routes.append("articles")

    try:
        from app.api.routes.ai import router as ai_router
        app.include_router(ai_router, prefix=api_v1_prefix)
        app.include_router(ai_router, prefix=api_prefix)
        app.include_router(ai_router, prefix="/ai")
        registered_routes.append("ai")
    except Exception as e:
        logger.warning(f"Failed to register ai route: {e}")
        failed_routes.append("ai")

    try:
        from app.api.routes.chat import router as chat_router
        app.include_router(chat_router, prefix=api_v1_prefix)
        app.include_router(chat_router, prefix=api_prefix)
        registered_routes.append("chat")
    except Exception as e:
        logger.warning(f"Failed to register chat route: {e}")
        failed_routes.append("chat")

    try:
        from app.api.routes.messages import router as messages_router
        app.include_router(messages_router, prefix=api_v1_prefix)
        app.include_router(messages_router, prefix=api_prefix)
        registered_routes.append("messages")
    except Exception as e:
        logger.warning(f"Failed to register messages route: {e}")
        failed_routes.append("messages")

    # =====================================================
    # 8. 管理路由
    # =====================================================
    app.include_router(admin_router)
    registered_routes.append("admin")

    logger.info(f"路由注册完成 - 成功: {len(registered_routes)} 个, 失败: {len(failed_routes)} 个")
    if registered_routes:
        logger.info(f"成功注册: {registered_routes}")
    if failed_routes:
        logger.info(f"注册失败: {failed_routes}")

def auto_discover_and_register(app):
    """自动发现并注册路由模块
    
    扫描 app/api/routes/ 下的所有 Python 模块，
    从每个模块中导入 router 并注册到 FastAPI 应用。
    """
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
    logger.info(f"Registered modules: {registered}")
    
    return registered
