<template>
  <div class="skeleton-container">
    <!-- 头部骨架 -->
    <div class="skeleton-header">
      <div class="skeleton-logo"></div>
      <div class="skeleton-nav">
        <div class="skeleton-nav-item" v-for="i in 5" :key="i"></div>
      </div>
      <div class="skeleton-actions">
        <div class="skeleton-btn"></div>
        <div class="skeleton-btn"></div>
      </div>
    </div>
    
    <!-- 主内容骨架 -->
    <div class="skeleton-main">
      <!-- Hero区域 -->
      <div class="skeleton-hero">
        <div class="skeleton-title"></div>
        <div class="skeleton-subtitle"></div>
        <div class="skeleton-actions-row">
          <div class="skeleton-action-btn primary"></div>
          <div class="skeleton-action-btn secondary"></div>
        </div>
      </div>
      
      <!-- 卡片区域 -->
      <div class="skeleton-cards">
        <div class="skeleton-card" v-for="i in 4" :key="i">
          <div class="skeleton-card-icon"></div>
          <div class="skeleton-card-title"></div>
          <div class="skeleton-card-desc"></div>
        </div>
      </div>
      
      <!-- 内容区域 -->
      <div class="skeleton-content">
        <div class="skeleton-section-title"></div>
        <div class="skeleton-list">
          <div class="skeleton-list-item" v-for="i in 3" :key="i">
            <div class="skeleton-list-image"></div>
            <div class="skeleton-list-content">
              <div class="skeleton-list-title"></div>
              <div class="skeleton-list-desc"></div>
              <div class="skeleton-list-meta">
                <div class="skeleton-list-tag" v-for="j in 2" :key="j"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部骨架 -->
    <div class="skeleton-footer">
      <div class="skeleton-footer-content">
        <div class="skeleton-footer-section" v-for="i in 3" :key="i">
          <div class="skeleton-footer-title"></div>
          <div class="skeleton-footer-links">
            <div class="skeleton-footer-link" v-for="j in 4" :key="j"></div>
          </div>
        </div>
      </div>
      <div class="skeleton-footer-bottom"></div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.skeleton-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #080810 0%, #12121f 50%, #1a1a32 100%);
}

.skeleton-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.skeleton-logo {
  width: 48px;
  height: 48px;
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 25%, rgba(102, 126, 234, 0.4) 50%, rgba(102, 126, 234, 0.2) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
}

.skeleton-nav {
  display: flex;
  gap: 16px;
}

.skeleton-nav-item {
  width: 60px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  animation: shimmer 1.5s infinite;
}

.skeleton-actions {
  display: flex;
  gap: 12px;
}

.skeleton-btn {
  width: 72px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  animation: shimmer 1.5s infinite;
}

.skeleton-hero {
  padding: 60px 24px;
  text-align: center;
}

.skeleton-title {
  width: 60%;
  height: 48px;
  margin: 0 auto 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  animation: shimmer 1.5s infinite;
}

.skeleton-subtitle {
  width: 40%;
  height: 24px;
  margin: 0 auto 32px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  animation: shimmer 1.5s infinite;
}

.skeleton-actions-row {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.skeleton-action-btn {
  width: 140px;
  height: 48px;
  border-radius: 12px;
  animation: shimmer 1.5s infinite;
}

.skeleton-action-btn.primary {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.3) 25%, rgba(102, 126, 234, 0.5) 50%, rgba(102, 126, 234, 0.3) 75%);
  background-size: 200% 100%;
}

.skeleton-action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
}

.skeleton-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 0 24px 40px;
}

.skeleton-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 24px;
}

.skeleton-card-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  margin-bottom: 16px;
  animation: shimmer 1.5s infinite;
}

.skeleton-card-title {
  width: 80%;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  margin-bottom: 8px;
  animation: shimmer 1.5s infinite;
}

.skeleton-card-desc {
  width: 100%;
  height: 16px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  padding: 0 24px 40px;
}

.skeleton-section-title {
  width: 200px;
  height: 28px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-bottom: 24px;
  animation: shimmer 1.5s infinite;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton-list-item {
  display: flex;
  gap: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  padding: 20px;
}

.skeleton-list-image {
  width: 120px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  flex-shrink: 0;
  animation: shimmer 1.5s infinite;
}

.skeleton-list-content {
  flex: 1;
}

.skeleton-list-title {
  width: 60%;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  margin-bottom: 8px;
  animation: shimmer 1.5s infinite;
}

.skeleton-list-desc {
  width: 100%;
  height: 16px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  margin-bottom: 12px;
  animation: shimmer 1.5s infinite;
}

.skeleton-list-meta {
  display: flex;
  gap: 8px;
}

.skeleton-list-tag {
  width: 60px;
  height: 24px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  animation: shimmer 1.5s infinite;
}

.skeleton-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 40px 24px 24px;
}

.skeleton-footer-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 24px;
}

.skeleton-footer-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-footer-title {
  width: 100px;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  animation: shimmer 1.5s infinite;
}

.skeleton-footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-footer-link {
  width: 80%;
  height: 16px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  animation: shimmer 1.5s infinite;
}

.skeleton-footer-bottom {
  height: 20px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

@media (max-width: 768px) {
  .skeleton-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .skeleton-footer-content {
    grid-template-columns: 1fr;
  }
  
  .skeleton-nav {
    display: none;
  }
  
  .skeleton-title {
    width: 90%;
  }
  
  .skeleton-subtitle {
    width: 70%;
  }
}
</style>