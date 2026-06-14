<template>
  <div class="legal-page">
    <div class="legal-container">
      <div class="legal-header">
        <h1>{{ title }}</h1>
        <p class="version">版本号：{{ version }} | 生效日期：{{ effectiveDate }}</p>
      </div>
      
      <div class="legal-content" v-html="content"></div>
      
      <div class="legal-footer">
        <p>如有疑问，请联系我们：service@xiaolongxia.com</p>
        <el-button type="primary" @click="goBack">返回</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

const docType = computed(() => route.params.type || 'terms')

const docInfo = {
  terms: {
    title: '用户服务协议',
    version: 'V1.0.0',
    effectiveDate: '2026年1月1日',
    file: '/docs/用户服务协议.md'
  },
  privacy: {
    title: '隐私政策',
    version: 'V1.0.0',
    effectiveDate: '2026年1月1日',
    file: '/docs/隐私政策.md'
  },
  copyright: {
    title: '版权声明',
    version: 'V1.0.0',
    effectiveDate: '2026年1月1日',
    file: '/docs/版权声明.md'
  },
  security: {
    title: '安全协议',
    version: 'V1.0.0',
    effectiveDate: '2026年1月1日',
    file: '/docs/安全协议.md'
  }
}

const title = computed(() => docInfo[docType.value]?.title || '法律文档')
const version = computed(() => docInfo[docType.value]?.version || 'V1.0.0')
const effectiveDate = computed(() => docInfo[docType.value]?.effectiveDate || '2026年1月1日')

const content = ref('')

const loadContent = async () => {
  try {
    const file = docInfo[docType.value]?.file
    if (file) {
      const response = await fetch(file)
      const text = await response.text()
      content.value = marked(text)
    }
  } catch (error) {
    content.value = '<p>文档加载失败，请稍后重试。</p>'
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadContent()
})
</script>

<style scoped>
.legal-page {
  min-height: 100vh;
  background: #1a1a2e;
  padding: 40px 20px;
}

.legal-container {
  max-width: 900px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.legal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  color: white;
  padding: 48px;
  text-align: center;
}

.legal-header h1 {
  margin: 0 0 12px 0;
  font-size: 32px;
  font-weight: 700;
}

.legal-header .version {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.legal-content {
  padding: 48px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.85);
}

.legal-content :deep(h1) {
  font-size: 24px;
  margin: 32px 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #667eea;
  color: #fff;
}

.legal-content :deep(h2) {
  font-size: 20px;
  margin: 28px 0 14px 0;
  color: #fff;
}

.legal-content :deep(h3) {
  font-size: 18px;
  margin: 24px 0 12px 0;
  color: rgba(255, 255, 255, 0.9);
}

.legal-content :deep(p) {
  margin: 12px 0;
}

.legal-content :deep(ul), .legal-content :deep(ol) {
  padding-left: 28px;
  margin: 12px 0;
}

.legal-content :deep(li) {
  margin: 10px 0;
}

.legal-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.legal-content :deep(th), .legal-content :deep(td) {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 14px;
  text-align: left;
}

.legal-content :deep(th) {
  background: rgba(255, 255, 255, 0.05);
  font-weight: 600;
  color: #fff;
}

.legal-content :deep(hr) {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 32px 0;
}

.legal-content :deep(strong) {
  color: #667eea;
}

.legal-content :deep(code) {
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 8px;
  border-radius: 6px;
  font-family: monospace;
  color: #f093fb;
}

.legal-content :deep(pre) {
  background: rgba(255, 255, 255, 0.03);
  padding: 20px;
  border-radius: 10px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.legal-content :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.legal-content :deep(a:hover) {
  text-decoration: underline;
}

.legal-footer {
  padding: 32px 48px;
  background: rgba(255, 255, 255, 0.02);
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.legal-footer p {
  margin: 0 0 16px 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.legal-footer :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  padding: 12px 32px;
}

.legal-footer :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .legal-page {
    padding: 20px 10px;
  }
  
  .legal-header {
    padding: 32px 20px;
  }
  
  .legal-header h1 {
    font-size: 24px;
  }
  
  .legal-content {
    padding: 24px;
  }
}
</style>
