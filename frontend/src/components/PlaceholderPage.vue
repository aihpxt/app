<template>
  <div class="placeholder-page">
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <p class="page-desc">{{ pageDesc }}</p>
      </div>
    </div>
    <div class="container">
      <div class="card">
        <h2>功能开发中</h2>
        <p>{{ pageName }}功能正在开发中，敬请期待！</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PlaceholderPage',
  props: {
    pageTitle: {
      type: String,
      default: '页面标题'
    },
    pageDesc: {
      type: String,
      default: '页面描述'
    },
    pageName: {
      type: String,
      default: '该'
    }
  }
}
</script>

<style scoped>
.placeholder-page {
  min-height: 100vh;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 0;
  color: white;
  margin-bottom: 40px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 10px;
}

.page-desc {
  font-size: 18px;
  opacity: 0.9;
}

.card {
  background: white;
  padding: 60px 40px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.card h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 15px;
}

.card p {
  font-size: 16px;
  color: #606266;
}
</style>
