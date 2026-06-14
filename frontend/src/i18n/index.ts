import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import en from './locales/en.json'
import zhYN from './locales/zh-YN.json'

const messages = {
  'zh-CN': zhCN,
  'en': en,
  'zh-YN': zhYN
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages
})

export default i18n
