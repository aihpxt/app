"""基础服务类"""

import logging
from abc import ABC, abstractmethod


class BaseService(ABC):
    """基础服务类"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return self.service_name
