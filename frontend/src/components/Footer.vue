<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p>© 2026 爱鹏航 保留所有权利</p>
    </div>
  </footer>
</template>

<script setup>
// Footer已简化为状态栏，主要版权信息在App.vue的status-bar中显示
// 此组件保留用于需要独立页脚的场景
</script>

<style scoped>
.app-footer {
  background: var(--wx-bg-light);
  border-top: 1px solid var(--wx-border-light);
  padding: 12px 0;
  text-align: center;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.footer-content p {
  margin: 0;
  font-size: 12px;
  color: var(--wx-text-muted);
}
</style>