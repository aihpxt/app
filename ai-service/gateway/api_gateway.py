#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一API网关
负责统一路由、认证、限流等功能
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import httpx
import json
import time
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """简单的限流器"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # 清理过期的请求记录
        self.requests[client_id] = [req_time for req_time in client_requests 
                                   if now - req_time < self.time_window]
        
        # 检查请求数量
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录请求
        self.requests[client_id].append(now)
        return True


class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services = {
            'ai-service': {
                'url': 'http://localhost:5001',
                'health': '/health',
                'timeout': 30.0
            },
            'call-center': {
                'url': 'http://localhost:5002',
                'health': '/health',
                'timeout': 30.0
            },
            'frontend': {
                'url': 'http://localhost:3000',
                'health': '/',
                'timeout': 10.0
            }
        }
    
    def get_service_url(self, service_name: str) -> str:
        """获取服务URL"""
        service = self.services.get(service_name)
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        return service['url']
    
    def register_service(self, service_name: str, url: str, health: str = '/health'):
        """注册服务"""
        self.services[service_name] = {
            'url': url,
            'health': health,
            'timeout': 30.0
        }
        logger.info(f"Service registered: {service_name} -> {url}")


class APIGateway:
    """API网关主类"""
    
    def __init__(self):
        self.app = FastAPI(title="统一API网关", version="1.0.0")
        self.rate_limiter = RateLimiter(max_requests=100, time_window=60)
        self.service_registry = ServiceRegistry()
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """设置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "统一API网关",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "services": list(self.service_registry.services.keys())
            }
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/services")
        async def list_services():
            return {
                "services": self.service_registry.services,
                "count": len(self.service_registry.services)
            }
        
        @self.app.post("/services/register")
        async def register_service(service_info: Dict[str, Any]):
            """注册新服务"""
            service_name = service_info.get('name')
            url = service_info.get('url')
            health = service_info.get('health', '/health')
            
            if not service_name or not url:
                raise HTTPException(status_code=400, detail="Service name and url are required")
            
            self.service_registry.register_service(service_name, url, health)
            return {"message": f"Service {service_name} registered successfully"}
        
        @self.app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_request(path: str, request: Request, x_client_id: Optional[str] = Header(None)):
            """代理请求到对应服务"""
            
            # 限流检查
            client_id = x_client_id or request.client.host
            if not self.rate_limiter.is_allowed(client_id):
                raise HTTPException(status_code=429, detail="Too many requests")
            
            # 确定目标服务
            service_name = self.determine_service(path)
            service_url = self.service_registry.get_service_url(service_name)
            
            # 构建目标URL
            target_url = f"{service_url}/api/{path}"
            
            # 转发请求
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # 获取请求体
                    body = await request.body()
                    
                    # 转发请求
                    response = await client.request(
                        method=request.method,
                        url=target_url,
                        headers=dict(request.headers),
                        content=body,
                        params=request.query_params
                    )
                    
                    # 返回响应
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code
                    )
            
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Service timeout")
            except httpx.ConnectError:
                raise HTTPException(status_code=503, detail="Service unavailable")
            except Exception as e:
                logger.error(f"Proxy error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.api_route("/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_ai_service(path: str, request: Request):
            """代理到AI服务"""
            return await self.proxy_to_service('ai-service', path, request)
        
        @self.app.api_route("/call-center/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_call_center(path: str, request: Request):
            """代理到电话系统"""
            return await self.proxy_to_service('call-center', path, request)
        
        @self.app.get("/metrics")
        async def metrics():
            """获取指标"""
            return {
                "rate_limiter": {
                    "max_requests": self.rate_limiter.max_requests,
                    "time_window": self.rate_limiter.time_window,
                    "active_clients": len(self.rate_limiter.requests)
                },
                "services": {
                    name: {
                        "url": service['url'],
                        "health": service['health']
                    }
                    for name, service in self.service_registry.services.items()
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def determine_service(self, path: str) -> str:
        """根据路径确定目标服务"""
        if path.startswith('agents') or path.startswith('chat'):
            return 'ai-service'
        elif path.startswith('call-center'):
            return 'call-center'
        elif path.startswith('schools') or path.startswith('policies'):
            return 'ai-service'
        else:
            return 'ai-service'
    
    async def proxy_to_service(self, service_name: str, path: str, request: Request):
        """代理到指定服务"""
        service_url = self.service_registry.get_service_url(service_name)
        target_url = f"{service_url}/{path}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                body = await request.body()
                
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=dict(request.headers),
                    content=body,
                    params=request.query_params
                )
                
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code
                )
        
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Service unavailable")
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


def create_gateway() -> FastAPI:
    """创建网关应用"""
    gateway = APIGateway()
    return gateway.app


if __name__ == '__main__':
    import uvicorn
    
    app = create_gateway()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
