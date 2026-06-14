#!/usr/bin/env python3
"""
SSL证书管理工具
支持证书生成、有效期检查、自动更新和Let's Encrypt集成
"""

import os
import sys
import subprocess
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SSLCertManager:
    """SSL证书管理器"""

    def __init__(self, cert_dir: str = "certs"):
        """
        初始化证书管理器
        
        Args:
            cert_dir: 证书存储目录
        """
        self.cert_dir = cert_dir
        os.makedirs(cert_dir, exist_ok=True)

    def generate_self_signed_cert(
        self,
        common_name: str = "localhost",
        country_name: str = "CN",
        state_or_province_name: str = "Yunnan",
        locality_name: str = "Kunming",
        organization_name: str = "AI School Platform",
        valid_days: int = 365
    ) -> Tuple[str, str]:
        """
        生成自签名SSL证书
        
        Args:
            common_name: 域名/主机名
            country_name: 国家代码
            state_or_province_name: 省份
            locality_name: 城市
            organization_name: 组织名称
            valid_days: 有效期天数
        
        Returns:
            (证书文件路径, 私钥文件路径)
        """
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # 设置证书有效期
        valid_from = datetime.datetime.utcnow()
        valid_to = valid_from + datetime.timedelta(days=valid_days)

        # 创建证书主题
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_province_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        # 构建证书
        cert_builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(valid_from)
            .not_valid_after(valid_to)
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(common_name)]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        # 保存证书和私钥
        cert_path = os.path.join(self.cert_dir, "server.crt")
        key_path = os.path.join(self.cert_dir, "server.key")

        with open(cert_path, "wb") as f:
            f.write(cert_builder.public_bytes(serialization.Encoding.PEM))

        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        logger.info(f"自签名证书已生成: {cert_path}, {key_path}")
        return cert_path, key_path

    def check_cert_expiry(self, cert_path: str) -> Optional[Dict[str, Any]]:
        """
        检查证书有效期
        
        Args:
            cert_path: 证书文件路径
        
        Returns:
            证书信息字典或None
        """
        if not os.path.exists(cert_path):
            return None

        with open(cert_path, "rb") as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        now = datetime.datetime.utcnow()
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        expires_in = (not_after - now).days

        subject = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        common_name = subject[0].value if subject else "Unknown"

        return {
            "common_name": common_name,
            "not_before": not_before.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "not_after": not_after.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "expires_in_days": expires_in,
            "is_valid": now >= not_before and now <= not_after,
            "is_expired": now > not_after,
            "is_about_to_expire": expires_in <= 30
        }

    def renew_cert(self, cert_path: str, key_path: str, valid_days: int = 365) -> bool:
        """
        更新证书（生成新证书但保留私钥）
        
        Args:
            cert_path: 证书文件路径
            key_path: 私钥文件路径
            valid_days: 新证书有效期天数
        
        Returns:
            是否更新成功
        """
        try:
            # 获取现有证书信息
            cert_info = self.check_cert_expiry(cert_path)
            if not cert_info:
                logger.error("无法读取现有证书")
                return False

            # 读取私钥
            with open(key_path, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )

            # 生成新证书
            valid_from = datetime.datetime.utcnow()
            valid_to = valid_from + datetime.timedelta(days=valid_days)

            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, cert_info["common_name"]),
            ])

            cert_builder = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(valid_from)
                .not_valid_after(valid_to)
                .add_extension(
                    x509.SubjectAlternativeName([x509.DNSName(cert_info["common_name"])]),
                    critical=False,
                )
                .sign(private_key, hashes.SHA256(), default_backend())
            )

            with open(cert_path, "wb") as f:
                f.write(cert_builder.public_bytes(serialization.Encoding.PEM))

            logger.info(f"证书已更新: {cert_path}")
            return True

        except Exception as e:
            logger.error(f"更新证书失败: {e}")
            return False

    def check_and_renew_cert(self, cert_path: str, key_path: str, renew_threshold_days: int = 30) -> bool:
        """
        检查并自动更新即将过期的证书
        
        Args:
            cert_path: 证书文件路径
            key_path: 私钥文件路径
            renew_threshold_days: 过期前多少天自动更新
        
        Returns:
            是否进行了更新
        """
        cert_info = self.check_cert_expiry(cert_path)
        if not cert_info:
            logger.warning("证书不存在，无法检查")
            return False

        if cert_info["is_about_to_expire"]:
            logger.info(f"证书即将过期（{cert_info['expires_in_days']}天后），正在更新...")
            return self.renew_cert(cert_path, key_path)

        logger.info(f"证书有效期正常（{cert_info['expires_in_days']}天后过期）")
        return False

    def generate_dh_params(self, size: int = 2048) -> str:
        """
        生成Diffie-Hellman参数
        
        Args:
            size: 参数大小
        
        Returns:
            DH参数文件路径
        """
        dh_path = os.path.join(self.cert_dir, "dhparam.pem")
        
        try:
            # 使用openssl命令生成DH参数
            subprocess.run(
                ["openssl", "dhparam", "-out", dh_path, str(size)],
                check=True,
                capture_output=True
            )
            logger.info(f"DH参数已生成: {dh_path}")
            return dh_path
        except subprocess.CalledProcessError as e:
            logger.error(f"生成DH参数失败: {e.stderr.decode()}")
            return ""

    def install_letsencrypt_cert(self, domain: str, email: str) -> bool:
        """
        使用Let's Encrypt安装证书（需要certbot）
        
        Args:
            domain: 域名
            email: 邮箱地址
        
        Returns:
            是否安装成功
        """
        try:
            # 检查certbot是否安装
            result = subprocess.run(
                ["certbot", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error("certbot未安装，请先安装certbot")
                return False

            # 获取证书
            result = subprocess.run(
                [
                    "certbot", "certonly", "--standalone",
                    "-d", domain,
                    "--email", email,
                    "--agree-tos",
                    "--non-interactive"
                ],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # 复制证书到指定目录
                cert_src = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
                key_src = f"/etc/letsencrypt/live/{domain}/privkey.pem"
                
                if os.path.exists(cert_src) and os.path.exists(key_src):
                    import shutil
                    shutil.copy(cert_src, os.path.join(self.cert_dir, "server.crt"))
                    shutil.copy(key_src, os.path.join(self.cert_dir, "server.key"))
                    logger.info(f"Let's Encrypt证书已安装: {domain}")
                    return True
                else:
                    logger.error("Let's Encrypt证书文件不存在")
                    return False
            else:
                logger.error(f"获取Let's Encrypt证书失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"安装Let's Encrypt证书失败: {e}")
            return False

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="SSL证书管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 生成自签名证书
    gen_parser = subparsers.add_parser("generate", help="生成自签名证书")
    gen_parser.add_argument("--domain", default="localhost", help="域名")
    gen_parser.add_argument("--days", type=int, default=365, help="有效期天数")

    # 检查证书
    check_parser = subparsers.add_parser("check", help="检查证书有效期")
    check_parser.add_argument("--cert", default="certs/server.crt", help="证书路径")

    # 更新证书
    renew_parser = subparsers.add_parser("renew", help="更新证书")
    renew_parser.add_argument("--cert", default="certs/server.crt", help="证书路径")
    renew_parser.add_argument("--key", default="certs/server.key", help="私钥路径")

    # 安装Let's Encrypt证书
    le_parser = subparsers.add_parser("letsencrypt", help="安装Let's Encrypt证书")
    le_parser.add_argument("--domain", required=True, help="域名")
    le_parser.add_argument("--email", required=True, help="邮箱")

    args = parser.parse_args()

    manager = SSLCertManager()

    if args.command == "generate":
        manager.generate_self_signed_cert(
            common_name=args.domain,
            valid_days=args.days
        )
        print(f"证书已生成到 {manager.cert_dir}")

    elif args.command == "check":
        info = manager.check_cert_expiry(args.cert)
        if info:
            print("证书信息:")
            print(f"  域名: {info['common_name']}")
            print(f"  有效期开始: {info['not_before']}")
            print(f"  有效期结束: {info['not_after']}")
            print(f"  剩余天数: {info['expires_in_days']} 天")
            print(f"  是否有效: {'是' if info['is_valid'] else '否'}")
            print(f"  是否过期: {'是' if info['is_expired'] else '否'}")
            print(f"  是否即将过期: {'是' if info['is_about_to_expire'] else '否'}")
        else:
            print(f"证书文件不存在: {args.cert}")

    elif args.command == "renew":
        if manager.check_and_renew_cert(args.cert, args.key):
            print("证书已更新")
        else:
            print("证书无需更新")

    elif args.command == "letsencrypt":
        if manager.install_letsencrypt_cert(args.domain, args.email):
            print("Let's Encrypt证书安装成功")
        else:
            print("Let's Encrypt证书安装失败")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()