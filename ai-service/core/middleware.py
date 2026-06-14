from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import settings
from .logger import logger

limiter = Limiter(key_func=get_remote_address)

def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    if settings.is_production:
        allowed_hosts = ["*"]
        for origin in settings.cors_origins_list:
            if "localhost" not in origin and "127.0.0.1" not in origin:
                host = origin.replace("https://", "").replace("http://", "")
                allowed_hosts.append(host)
        
        if len(allowed_hosts) > 1:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=allowed_hosts
            )
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import time
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        log_message = f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        
        if response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Server"] = settings.APP_NAME
        
        return response
