# Kubernetes 部署指南

## 部署步骤

### 1. 创建命名空间
```bash
kubectl apply -f namespace.yaml
```

### 2. 部署MySQL
```bash
kubectl apply -f mysql-deployment.yaml
```

### 3. 部署Redis
```bash
kubectl apply -f redis-deployment.yaml
```

### 4. 部署后端服务
```bash
kubectl apply -f backend-deployment.yaml
```

### 5. 部署AI服务
```bash
kubectl apply -f ai-service-deployment.yaml
```

### 6. 部署前端服务
```bash
kubectl apply -f frontend-deployment.yaml
```

### 7. 部署Ingress
```bash
kubectl apply -f ingress.yaml
```

### 8. 一键部署
```bash
kubectl apply -f .
```

## 查看部署状态

```bash
# 查看所有Pod
kubectl get pods -n yunnan-ai-school

# 查看所有服务
kubectl get services -n yunnan-ai-school

# 查看所有部署
kubectl get deployments -n yunnan-ai-school

# 查看Ingress
kubectl get ingress -n yunnan-ai-school
```

## 访问应用

配置本地hosts文件，添加：
```
127.0.0.1 yunnan-ai-school.local
```

然后访问：http://yunnan-ai-school.local

## 扩展服务

```bash
# 扩展后端服务到3个副本
kubectl scale deployment backend --replicas=3 -n yunnan-ai-school

# 扩展AI服务到3个副本
kubectl scale deployment ai-service --replicas=3 -n yunnan-ai-school
```

## 删除部署

```bash
kubectl delete -f .
```