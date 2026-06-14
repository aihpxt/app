# Kubernetes 部署回滚方案

## 概述
本文档描述了云南省AI中考择校平台在Kubernetes集群上的部署回滚方案，确保在出现部署问题时能够快速恢复到之前的稳定版本。

## 回滚场景

### 场景1: 部署失败
- Pod无法启动（镜像拉取失败、配置错误、依赖缺失）
- 容器启动后立即崩溃
- 健康检查失败

### 场景2: 应用异常
- 应用运行异常（内存泄漏、CPU占用过高）
- 功能回归（新版本引入bug）
- 性能下降

### 场景3: 数据问题
- 数据库迁移失败
- 数据损坏

## 回滚准备

### 1. 确保部署历史可用
Kubernetes Deployment默认保留最近的部署历史（默认保留10个版本）。

```bash
# 查看部署历史
kubectl rollout history deployment/backend -n yunnan-ai-school
```

### 2. 检查当前状态
```bash
# 检查部署状态
kubectl rollout status deployment/backend -n yunnan-ai-school

# 检查Pod状态
kubectl get pods -n yunnan-ai-school -l app=backend
```

## 回滚操作步骤

### 步骤1: 回滚到上一个版本

```bash
# 回滚到上一个稳定版本
kubectl rollout undo deployment/backend -n yunnan-ai-school
```

### 步骤2: 回滚到指定版本

```bash
# 查看历史版本
kubectl rollout history deployment/backend -n yunnan-ai-school

# 回滚到指定版本（例如版本3）
kubectl rollout undo deployment/backend -n yunnan-ai-school --to-revision=3
```

### 步骤3: 验证回滚结果

```bash
# 检查回滚状态
kubectl rollout status deployment/backend -n yunnan-ai-school

# 检查Pod状态
kubectl get pods -n yunnan-ai-school -l app=backend

# 检查服务是否正常
kubectl get services -n yunnan-ai-school

# 测试API接口
curl -X GET http://<service-ip>:8080/api/health
```

### 步骤4: 回滚其他组件

**前端服务回滚：**
```bash
kubectl rollout undo deployment/frontend -n yunnan-ai-school
```

**AI服务回滚：**
```bash
kubectl rollout undo deployment/ai-service -n yunnan-ai-school
```

## 紧急回滚流程（5分钟内完成）

```
1. 检测问题（监控告警或用户反馈）
       ↓
2. 确认问题范围和影响
       ↓
3. 执行回滚命令
       ↓
4. 验证回滚结果
       ↓
5. 通知相关人员
       ↓
6. 分析问题原因
```

## 回滚验证清单

- [ ] Pod状态正常（Running）
- [ ] 健康检查通过
- [ ] 服务端口正常监听
- [ ] API接口响应正常
- [ ] 数据库连接正常
- [ ] Redis连接正常
- [ ] 日志无错误信息
- [ ] 监控指标恢复正常

## 回滚时间预估

| 组件 | 回滚时间 |
|------|----------|
| Backend | ~30秒 |
| Frontend | ~30秒 |
| AI Service | ~45秒 |
| 全部组件 | ~2分钟 |

## 注意事项

1. **数据一致性**: 回滚前确保数据库数据不会因版本回退而损坏
2. **配置文件**: 回滚时配置文件也需要同步回退
3. **缓存清理**: 回滚后可能需要清理Redis缓存
4. **流量切换**: 确保在回滚过程中流量正常切换

## 日志与监控

```bash
# 查看Pod日志
kubectl logs -n yunnan-ai-school -l app=backend --follow

# 查看事件
kubectl get events -n yunnan-ai-school

# Prometheus监控
# 访问: http://<prometheus-ip>:9090
```

## 联系人

| 角色 | 姓名 | 联系方式 |
|------|------|----------|
| 运维负责人 | 张三 | 13800138000 |
| 开发负责人 | 李四 | 13900139000 |
| 紧急联系人 | 王五 | 13700137000 |

## 版本记录

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| v1.0 | 2026-05-24 | DevOps | 初始版本 |