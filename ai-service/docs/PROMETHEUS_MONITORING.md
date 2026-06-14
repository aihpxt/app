# Prometheus监控集成说明

## 功能概述

Prometheus监控集成提供以下功能：

1. **HTTP请求监控** - 记录请求数量、延迟、状态码
2. **业务指标** - 记录业务操作、预测请求等
3. **缓存监控** - 缓存命中率和未命中率
4. **外部API调用** - 记录对外部服务的调用
5. **系统信息** - 数据库连接、Redis状态等

## 暴露的指标

### HTTP指标

- `http_requests_total` - HTTP请求总数
- `http_request_duration_seconds` - HTTP请求延迟
- `http_requests_in_progress` - 正在处理的请求数

### 业务指标

- `business_operations_total` - 业务操作总数
- `prediction_requests_total` - 预测请求总数
- `user_active_count` - 活跃用户数

### 缓存指标

- `cache_hits_total` - 缓存命中总数
- `cache_misses_total` - 缓存未命中总数

### 外部API指标

- `external_api_calls_total` - 外部API调用总数
- `external_api_duration_seconds` - 外部API调用延迟

## API接口

### 获取Prometheus指标

```bash
GET /api/metrics/prometheus
```

### 获取指标摘要

```bash
GET /api/metrics/summary
```

返回示例：
```json
{
  "cache_hit_rate": "85.50%",
  "active_users": 42,
  "redis_connected": true,
  "db_active_connections": 5,
  "db_idle_connections": 10
}
```

### 健康检查

```bash
GET /api/metrics/health
```

## Prometheus配置

配置文件：`prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ai-service'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/api/metrics/prometheus'
    scrape_interval: 10s
```

## 启动Prometheus

```bash
# 方式1: 使用脚本启动
python scripts/start_prometheus.py

# 方式2: 手动启动
prometheus --config.file prometheus.yml

# 方式3: 使用Docker
docker run -d --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

## Grafana集成

建议使用Grafana进行可视化展示：

1. 添加Prometheus数据源
2. 创建仪表板
3. 导入常用模板（如Node Exporter Full、FastAPI监控等）

## 常用PromQL查询

### 请求率
```promql
rate(http_requests_total[5m])
```

### 错误率
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### P99延迟
```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### 缓存命中率
```promql
sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m])))
```

## 告警规则示例

```yaml
groups:
  - name: ai-service-alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: ServiceDown
        expr: up{job="ai-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI Service is down"
```
