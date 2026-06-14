"""主应用模块 - 简化版，确保核心功能正常运行"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import APP_NAME, APP_VERSION, DEBUG, ALLOWED_ORIGINS

try:
    import app.core.logging
except Exception:
    pass

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例（简化版）"""
    
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="AI服务API",
        debug=DEBUG
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 配置Gzip压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 初始化数据库
    try:
        from app.core.database_pool import get_db_manager
        get_db_manager()
    except Exception as e:
        logger.warning(f"数据库初始化失败: {e}")
    
    # 注册路由（只注册核心 auth 路由，确保核心功能可用）
    try:
        from app.api.routes import register_routes
        register_routes(app)
        logger.info(f"路由注册成功，共 {len(app.routes)} 个路由")
    except Exception as e:
        logger.error(f"路由注册失败: {e}", exc_info=True)
        # 尝试只注册 auth 路由
        try:
            from app.api.routes.auth import router as auth_router
            app.include_router(auth_router, prefix="/api/user", tags=["用户认证"])
            app.include_router(auth_router, prefix="/api/v1/auth", tags=["用户认证-v1"])
            logger.info("仅注册 auth 路由成功")
        except Exception as e2:
            logger.error(f"auth 路由注册也失败: {e2}", exc_info=True)
    
    logger.info(f"应用初始化完成: {APP_NAME} v{APP_VERSION}")
    return app
