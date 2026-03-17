import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate' // Pinia持久化插件（解决刷新丢失状态）
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import '@/styles/common.scss'

const app = createApp(App)
const pinia = createPinia()
//注册持久化插件
pinia.use(piniaPluginPersistedstate)

app.use(pinia)

app.use(createPinia())
app.use(router)

app.mount('#app')
