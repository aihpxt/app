# SSL/TLS证书配置说明

## 快速开始

### 1. 生成自签名证书（仅用于开发和测试）

```bash
python scripts/ssl_cert_manager.py generate --domain localhost --days 365
```

### 2. 配置环境变量

在生产环境中，建议使用环境变量配置SSL：

```bash
# 启用HTTPS
export HTTPS_ENABLED=true

# 证书文件路径
export SSL_CERT_FILE=/path/to/server.crt
export SSL_KEY_FILE=/path/to/server.key

# 可选：客户端证书验证
export SSL_CA_FILE=/path/to/ca.crt
export SSL_VERIFY_CLIENT=true
```

### 3. 使用Let's Encrypt证书（生产环境）

建议使用Let's Encrypt自动证书：

```bash
# 使用certbot获取证书
certbot certonly --nginx -d yourdomain.com

# 配置环境变量
export HTTPS_ENABLED=true
export SSL_CERT_FILE=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
export SSL_KEY_FILE=/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

## 证书文件位置

```
ai-service/
└── certs/
    ├── server.crt      # 服务器证书
    ├── server.key      # 私钥
    ├── dhparam.pem     # DH参数（可选）
    └── backup/         # 证书备份
```

## HTTPS启动

使用支持HTTPS的启动脚本：

```bash
python start_service_https.py
```

或手动启动：

```bash
uvicorn app.core.app:app \
    --host 0.0.0.0 \
    --port 8001 \
    --ssl-certfile certs/server.crt \
    --ssl-keyfile certs/server.key
```

## 证书续期

自签名证书续期：

```bash
python scripts/ssl_cert_manager.py renew --domain localhost --days 365
```

## 安全建议

1. **生产环境**: 使用Let's Encrypt或商业CA签发的证书
2. **私钥保护**: 确保私钥文件权限设置为600
3. **证书有效期**: 建议使用90天的Let's Encrypt证书并设置自动续期
4. **TLS版本**: 禁用SSLv2、SSLv3和TLS 1.0/1.1，只使用TLS 1.2+
5. **客户端验证**: 对于高安全需求场景，启用双向TLS验证
