import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import i18n from './i18n'

import './assets/styles/enhanced.css'
import 'element-plus/dist/index.css'
import { initPerformanceMonitoring, initWebVitals } from './utils/performance'

initPerformanceMonitoring()

const app = createApp(App)

app.use(store)
app.use(router)
app.use(i18n)

app.config.errorHandler = (err: unknown, _vm: unknown, info: string) => {
  console.error('Vue错误:', err, info)
}

app.mount('#app')

initWebVitals()