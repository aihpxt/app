"""HTTPS和SSL证书配置"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class SSLConfig:
    """SSL配置数据类"""
    enabled: bool
    cert_file: str
    key_file: str
    ca_file: Optional[str] = None
    verify_client: bool = False
    ssl_version: str = "TLSv1.2"

class HTTPSConfig:
    """HTTPS配置管理"""

    def __init__(self):
        self.enabled = os.getenv("HTTPS_ENABLED", "false").lower() == "true"
        self.cert_file = os.getenv("SSL_CERT_FILE", "certs/server.crt")
        self.key_file = os.getenv("SSL_KEY_FILE", "certs/server.key")
        self.ca_file = os.getenv("SSL_CA_FILE", "")
        self.verify_client = os.getenv("SSL_VERIFY_CLIENT", "false").lower() == "true"
        self.ssl_version = os.getenv("SSL_VERSION", "TLSv1.2")

        self._validate_paths()

    def _validate_paths(self):
        """验证证书文件路径"""
        if self.enabled:
            if not os.path.exists(self.cert_file):
                raise FileNotFoundError(f"SSL证书文件不存在: {self.cert_file}")
            if not os.path.exists(self.key_file):
                raise FileNotFoundError(f"SSL私钥文件不存在: {self.key_file}")
            if self.verify_client and self.ca_file and not os.path.exists(self.ca_file):
                raise FileNotFoundError(f"SSL CA证书文件不存在: {self.ca_file}")

    def get_ssl_config(self) -> Optional[dict]:
        """获取SSL配置字典"""
        if not self.enabled:
            return None

        ssl_config = {
            "certfile": self.cert_file,
            "keyfile": self.key_file,
        }

        if self.verify_client and self.ca_file:
            ssl_config["ca_certs"] = self.ca_file
            ssl_config["cert_reqs"] = 2  # ssl.CERT_REQUIRED

        return ssl_config

    def is_valid(self) -> bool:
        """检查配置是否有效"""
        if not self.enabled:
            return True

        return (
            os.path.exists(self.cert_file) and
            os.path.exists(self.key_file) and
            (not self.verify_client or (self.ca_file and os.path.exists(self.ca_file)))
        )

def get_https_config() -> HTTPSConfig:
    """获取HTTPS配置实例"""
    return HTTPSConfig()
