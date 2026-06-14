"""OpenClaw 小龙虾 AI 网关"""

import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class OpenClawGateway:
    """OpenClaw 小龙虾 AI 网关
    
    负责管理和调度OpenClaw模块的各种服务，是OpenClaw模块的核心协调器。
    主要功能包括：
    1. 服务注册和管理
    2. 权限控制和管理
    3. 请求调度和处理
    4. 缓存机制，提高性能
    5. 错误处理和传递
    6. 健康检查和状态监控
    7. 监控和统计
    """
    
    def __init__(self):
        """初始化OpenClaw Gateway
        
        初始化服务存储、权限存储、日志记录器、请求计数器和缓存机制。
        """
        self.services = {}  # 服务存储
        self.permissions = {}  # 权限存储
        self.logger = self._setup_logger()  # 日志记录器
        self.request_counter = 0  # 请求计数器
        
        # 缓存机制
        self.cache = {}  # 缓存存储
        self.cache_expiry = 3600  # 缓存过期时间，单位：秒（1小时）
        self.last_cache_cleanup = time.time()  # 最后缓存清理时间
        self.cache_cleanup_interval = 600  # 缓存清理间隔，单位：秒（10分钟）
        self.cache_max_size = 1000  # 缓存最大条目数
        self.cache_hits = 0  # 缓存命中次数
        self.cache_misses = 0  # 缓存未命中次数
        
        # 监控统计
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0,
            "request_times": {},  # 请求类型对应的响应时间
            "error_types": {},  # 错误类型统计
            "service_calls": {}  # 服务调用统计
        }
        self.start_time = time.time()  # 服务启动时间
    
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('OpenClawGateway')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def register_service(self, service_name: str, service):
        """注册服务"""
        self.services[service_name] = service
        self.logger.info(f"服务注册成功: {service_name}")
    
    def set_permission(self, user_role: str, permissions: list):
        """设置权限"""
        self.permissions[user_role] = permissions
        self.logger.info(f"权限设置成功: {user_role}")
    
    def dispatch(self, service_name: str, method: str, params: Dict[str, Any], user_role: str = 'user') -> Dict[str, Any]:
        """调度服务"""
        self.request_counter += 1
        request_id = f"req_{int(time.time())}_{self.request_counter}"
        start_time = time.time()
        
        # 清理过期缓存
        self.cleanup_expired_cache()
        
        # 监控统计 - 开始
        self.metrics["total_requests"] += 1
        
        try:
            # 权限检查
            if not self._check_permission(user_role, service_name, method):
                error_response = {
                    "success": False,
                    "error": "权限不足",
                    "request_id": request_id,
                    "error_code": "PERMISSION_DENIED",
                    "error_details": f"用户角色 {user_role} 没有权限调用 {service_name}.{method}"
                }
                self.logger.warning(f"权限检查失败: {error_response['error_details']}")
                
                # 监控统计 - 失败
                self.metrics["failed_requests"] += 1
                error_type = "PERMISSION_DENIED"
                self.metrics["error_types"][error_type] = self.metrics["error_types"].get(error_type, 0) + 1
                
                return error_response
            
            # 服务调用
            if service_name not in self.services:
                error_response = {
                    "success": False,
                    "error": f"服务不存在: {service_name}",
                    "request_id": request_id,
                    "error_code": "SERVICE_NOT_FOUND",
                    "error_details": f"服务 {service_name} 未注册"
                }
                self.logger.warning(f"服务不存在: {service_name}")
                
                # 监控统计 - 失败
                self.metrics["failed_requests"] += 1
                error_type = "SERVICE_NOT_FOUND"
                self.metrics["error_types"][error_type] = self.metrics["error_types"].get(error_type, 0) + 1
                
                return error_response
            
            service = self.services[service_name]
            method_obj = getattr(service, method, None)
            if not method_obj:
                error_response = {
                    "success": False,
                    "error": f"方法不存在: {method}",
                    "request_id": request_id,
                    "error_code": "METHOD_NOT_FOUND",
                    "error_details": f"方法 {method} 在服务 {service_name} 中不存在"
                }
                self.logger.warning(f"方法不存在: {method} in {service_name}")
                
                # 监控统计 - 失败
                self.metrics["failed_requests"] += 1
                error_type = "METHOD_NOT_FOUND"
                self.metrics["error_types"][error_type] = self.metrics["error_types"].get(error_type, 0) + 1
                
                return error_response
            
            # 生成缓存键
            cache_key = self.get_cache_key(service_name, method, params)
            
            # 检查缓存
            cached_result = self.get_cache(cache_key)
            if cached_result is not None:
                self.logger.info(f"缓存命中: {service_name}.{method}, request_id: {request_id}")
                
                # 监控统计 - 成功
                self.metrics["successful_requests"] += 1
                response_time = time.time() - start_time
                self.metrics["total_response_time"] += response_time
                
                # 服务调用统计
                service_method = f"{service_name}.{method}"
                if service_method not in self.metrics["service_calls"]:
                    self.metrics["service_calls"][service_method] = {
                        "count": 0,
                        "total_time": 0,
                        "success_count": 0,
                        "failed_count": 0
                    }
                self.metrics["service_calls"][service_method]["count"] += 1
                self.metrics["service_calls"][service_method]["total_time"] += response_time
                self.metrics["service_calls"][service_method]["success_count"] += 1
                
                return {
                    "success": True,
                    "data": cached_result,
                    "request_id": request_id,
                    "execution_time": 0,
                    "cached": True
                }
            
            # 执行方法
            method_start_time = time.time()
            result = method_obj(**params)
            method_end_time = time.time()
            execution_time = method_end_time - method_start_time
            
            # 存入缓存
            self.set_cache(cache_key, result)
            
            # 记录日志
            self.logger.info(f"请求处理完成: {service_name}.{method}, 耗时: {execution_time:.3f}s, request_id: {request_id}")
            
            # 监控统计 - 成功
            self.metrics["successful_requests"] += 1
            response_time = time.time() - start_time
            self.metrics["total_response_time"] += response_time
            
            # 服务调用统计
            service_method = f"{service_name}.{method}"
            if service_method not in self.metrics["service_calls"]:
                self.metrics["service_calls"][service_method] = {
                    "count": 0,
                    "total_time": 0,
                    "success_count": 0,
                    "failed_count": 0
                }
            self.metrics["service_calls"][service_method]["count"] += 1
            self.metrics["service_calls"][service_method]["total_time"] += execution_time
            self.metrics["service_calls"][service_method]["success_count"] += 1
            
            return {
                "success": True,
                "data": result,
                "request_id": request_id,
                "execution_time": execution_time,
                "cached": False
            }
        except Exception as e:
            error_type = type(e).__name__
            error_response = {
                "success": False,
                "error": str(e),
                "request_id": request_id,
                "error_code": error_type.upper(),
                "error_details": f"执行 {service_name}.{method} 时发生错误: {str(e)}"
            }
            self.logger.error(f"请求处理失败: {error_response['error_details']}, request_id: {request_id}")
            
            # 监控统计 - 失败
            self.metrics["failed_requests"] += 1
            self.metrics["error_types"][error_type] = self.metrics["error_types"].get(error_type, 0) + 1
            
            # 服务调用统计
            service_method = f"{service_name}.{method}"
            if service_method not in self.metrics["service_calls"]:
                self.metrics["service_calls"][service_method] = {
                    "count": 0,
                    "total_time": 0,
                    "success_count": 0,
                    "failed_count": 0
                }
            self.metrics["service_calls"][service_method]["count"] += 1
            self.metrics["service_calls"][service_method]["failed_count"] += 1
            
            return error_response
    
    def _check_permission(self, user_role: str, service_name: str, method: str) -> bool:
        """检查权限"""
        # 管理员拥有所有权限
        if user_role == 'admin':
            return True
        
        # 获取用户角色的权限
        user_permissions = self.permissions.get(user_role, [])
        
        # 检查具体权限
        required_permission = f"{service_name}:{method}"
        if required_permission in user_permissions:
            return True
        
        # 检查服务级权限
        service_permission = f"{service_name}:*"
        if service_permission in user_permissions:
            return True
        
        # 检查全局权限
        global_permission = "*:*"
        if global_permission in user_permissions:
            return True
        
        self.logger.warning(f"权限检查失败: user_role={user_role}, service={service_name}, method={method}")
        return False
    
    def add_permission(self, user_role: str, permission: str):
        """添加权限"""
        if user_role not in self.permissions:
            self.permissions[user_role] = []
        if permission not in self.permissions[user_role]:
            self.permissions[user_role].append(permission)
            self.logger.info(f"权限添加成功: {user_role} -> {permission}")
    
    def remove_permission(self, user_role: str, permission: str):
        """移除权限"""
        if user_role in self.permissions and permission in self.permissions[user_role]:
            self.permissions[user_role].remove(permission)
            self.logger.info(f"权限移除成功: {user_role} -> {permission}")
    
    def get_permissions(self, user_role: str) -> list:
        """获取角色权限"""
        return self.permissions.get(user_role, [])
    
    def list_roles(self) -> list:
        """列出所有角色"""
        return list(self.permissions.keys())
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            "services": list(self.services.keys()),
            "permissions": self.permissions,
            "request_counter": self.request_counter,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        return status
    
    def cleanup_expired_cache(self):
        """清理过期的缓存"""
        current_time = time.time()
        
        # 检查是否需要清理
        if current_time - self.last_cache_cleanup < self.cache_cleanup_interval:
            return
        
        # 清理过期缓存
        expired_keys = []
        for key, (value, timestamp) in self.cache.items():
            if current_time - timestamp > self.cache_expiry:
                expired_keys.append(key)
        
        # 删除过期缓存
        for key in expired_keys:
            del self.cache[key]
        
        # 更新最后清理时间
        self.last_cache_cleanup = current_time
        
        if expired_keys:
            self.logger.info(f"清理了 {len(expired_keys)} 个过期缓存")
    
    def get_cache_key(self, service_name: str, method: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        import hashlib
        key_data = f"{service_name}:{method}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_expiry:
                self.cache_hits += 1
                return value
            else:
                # 缓存已过期，删除
                del self.cache[key]
                self.cache_misses += 1
        else:
            self.cache_misses += 1
        return None
    
    def set_cache(self, key: str, value: Any):
        """设置缓存"""
        # 检查缓存大小，如果超过最大限制，删除最旧的缓存条目
        if len(self.cache) >= self.cache_max_size:
            # 按时间戳排序，删除最旧的条目
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            oldest_key = sorted_items[0][0]
            del self.cache[oldest_key]
            self.logger.info(f"缓存大小超过限制，删除最旧的缓存条目: {oldest_key}")
        
        # 设置新的缓存条目
        self.cache[key] = (value, time.time())
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        # 检查服务状态
        service_status = {}
        for service_name, service in self.services.items():
            try:
                # 尝试调用服务的健康检查方法（如果存在）
                if hasattr(service, 'health_check'):
                    service_status[service_name] = service.health_check()
                else:
                    service_status[service_name] = {"status": "healthy", "message": "服务正常"}
            except Exception as e:
                service_status[service_name] = {"status": "unhealthy", "message": str(e)}
        
        # 检查缓存状态
        cache_status = {
            "size": len(self.cache),
            "expiry": self.cache_expiry,
            "last_cleanup": time.time() - self.last_cache_cleanup
        }
        
        # 检查权限状态
        permission_status = {
            "roles": len(self.permissions),
            "total_permissions": sum(len(perms) for perms in self.permissions.values())
        }
        
        # 整体健康状态
        overall_status = "healthy"
        for status in service_status.values():
            if status.get("status") != "healthy":
                overall_status = "degraded"
                break
        
        return {
            "status": overall_status,
            "services": len(self.services),
            "service_status": service_status,
            "cache": cache_status,
            "permissions": permission_status,
            "request_counter": self.request_counter,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # 计算平均响应时间
        if self.metrics["total_requests"] > 0:
            avg_response_time = self.metrics["total_response_time"] / self.metrics["total_requests"]
        else:
            avg_response_time = 0
        
        # 计算成功率
        if self.metrics["total_requests"] > 0:
            success_rate = self.metrics["successful_requests"] / self.metrics["total_requests"] * 100
        else:
            success_rate = 0
        
        # 服务调用统计
        service_metrics = {}
        for service_method, stats in self.metrics["service_calls"].items():
            if stats["count"] > 0:
                service_metrics[service_method] = {
                    "count": stats["count"],
                    "success_count": stats["success_count"],
                    "failed_count": stats["failed_count"],
                    "success_rate": stats["success_count"] / stats["count"] * 100,
                    "avg_response_time": stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
                }
        
        # 计算缓存命中率
        total_cache_operations = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0
        
        return {
            "uptime": uptime,
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "error_types": self.metrics["error_types"],
            "service_metrics": service_metrics,
            "cache_size": len(self.cache),
            "cache_max_size": self.cache_max_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "service_count": len(self.services),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

# 全局网关实例
gateway = OpenClawGateway()