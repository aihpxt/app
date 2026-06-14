import { createPinia } from 'pinia'

const store = createPinia()

export default store
export { useUserStore } from './modules/userStore'
export { useSchoolStore } from './modules/schoolStore'
export { useAiStore } from './modules/aiStore'