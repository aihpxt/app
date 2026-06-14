# 前端性能优化指南

## 概述

本文档记录了AI服务平台前端性能优化的实施情况和建议。

---

## 当前优化措施

### 1. 构建优化 (vite.config.js)

#### 代码分割
```javascript
manualChunks: {
  'element-plus': ['element-plus'],
  'echarts': ['echarts', 'vue-echarts'],
  'marked': ['marked'],
  'axios': ['axios'],
  'pinia': ['pinia']
}
```
- 将大型库分离成独立的chunk
- 按需加载，减少初始bundle大小

#### 资源压缩
```javascript
terserOptions: {
  compress: {
    drop_console: true,
    drop_debugger: true,
    pure_funcs: ['console.log', 'console.warn', 'console.error']
  }
}
```
- 移除console和debugger语句
- 压缩JavaScript代码

#### Gzip压缩
```javascript
viteCompression({
  algorithm: 'gzip',
  threshold: 10240, // 10KB以上才压缩
  deleteOriginFile: false,
  minRatio: 0.8
})
```
- 启用Gzip压缩
- 减少网络传输体积

---

## 建议的额外优化

### 2. 图片优化

#### 当前状态
项目使用静态图片，位于 `/public/images/` 目录

#### 建议措施
1. **图片压缩**
   - 使用WebP格式替代JPEG/PNG
   - 使用工具压缩现有图片
   - 添加响应式图片（srcset）

2. **懒加载**
   ```javascript
   // 使用vue-lazyload插件
   Vue.use(VueLazyload, {
     loading: '/images/placeholder.png',
     attempt: 1
   })
   ```

3. **CDN分发**
   - 将图片部署到CDN
   - 配置图片域名CDN加速

### 3. 路由懒加载

#### 当前状态
大部分路由使用静态导入

#### 建议措施
```javascript
// 修改 router/index.js
const routes = [
  {
    path: '/school',
    component: () => import('./views/School.vue') // 懒加载
  },
  {
    path: '/policy',
    component: () => import('./views/Policy.vue') // 懒加载
  }
]
```

### 4. 缓存策略

#### 当前配置
- JavaScript文件使用hash命名
- CSS文件使用hash命名

#### 建议增强
```javascript
// vite.config.js
build: {
  rollupOptions: {
    output: {
      manualChunks: (id) => {
        if (id.includes('node_modules')) {
          return 'vendor'
        }
      }
    }
  }
}
```

### 5. 预加载优化

#### 建议措施
```html
<!-- 在index.html添加 -->
<link rel="preload" href="/js/main.js" as="script">
<link rel="dns-prefetch" href="//cdn.example.com">
```

### 6. Service Worker

#### 建议措施
1. 使用Workbox实现Service Worker
2. 配置离线缓存策略
3. 实现增量更新

```javascript
// workbox-config.js
module.exports = {
  globDirectory: 'dist/',
  globPatterns: ['**/*.{js,css,html,png,jpg}'],
  swDest: 'dist/sw.js',
  clientsClaim: true,
  skipWaiting: true
}
```

---

## 性能测试建议

### 使用Lighthouse
```bash
# 安装lighthouse
npm install -g lighthouse

# 运行测试
lighthouse http://localhost:3001 --view
```

### 性能指标目标

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| First Contentful Paint (FCP) | < 1.8s | 待测试 |
| Largest Contentful Paint (LCP) | < 2.5s | 待测试 |
| Time to Interactive (TTI) | < 3.5s | 待测试 |
| Cumulative Layout Shift (CLS) | < 0.1 | 待测试 |
| First Input Delay (FID) | < 100ms | 待测试 |

---

## 监控和优化

### 性能监控工具
1. **Google PageSpeed Insights**
   - 在线性能测试
   - 移动端性能评估

2. **Web Vitals**
   ```javascript
   import { getCLS, getFID, getLCP } from 'web-vitals'

   function sendToAnalytics({ name, delta, id }) {
     console.log(`${name}: ${delta}`)
   }

   getCLS(sendToAnalytics)
   getFID(sendToAnalytics)
   getLCP(sendToAnalytics)
   ```

3. **Sentry**
   - 错误监控
   - 性能监控
   - 用户行为追踪

---

## 实施建议

### 第一阶段：基础优化（1天）
- [x] 代码分割配置
- [x] Gzip压缩配置
- [x] terser压缩配置
- [ ] 图片优化和压缩
- [ ] 路由懒加载

### 第二阶段：高级优化（2天）
- [ ] CDN配置
- [ ] Service Worker实现
- [ ] 性能监控集成
- [ ] 缓存策略优化

### 第三阶段：持续优化（持续）
- [ ] 定期性能测试
- [ ] 监控指标告警
- [ ] 用户反馈收集
- [ ] 持续优化迭代

---

## 总结

当前前端项目已经具备基本的性能优化措施，包括：
- ✅ 代码分割
- ✅ Gzip压缩
- ✅ terser压缩
- ✅ CSS代码分割
- ✅ 资源hash命名

建议的后续优化包括：
- ⏳ 图片优化
- ⏳ 路由懒加载
- ⏳ CDN配置
- ⏳ Service Worker
- ⏳ 性能监控

通过实施这些优化，可以显著提升页面加载速度和用户体验。
