import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import './styles/element-override.css'
import App from './App.vue'
import router from './router'
import './styles/design-tokens.css'
import './styles/global.css'
import './styles/transitions.css'

// === 主题初始化：在 Vue 渲染前应用 data-theme ===
;(function initTheme() {
  const saved = localStorage.getItem('theme') || 'system'
  if (saved === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else if (saved === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      document.documentElement.setAttribute('data-theme', 'dark')
    }
  }
  // 'light' => no attribute needed
})()

// === 监听系统主题变化 ===
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  const saved = localStorage.getItem('theme') || 'system'
  if (saved === 'system') {
    if (e.matches) {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
    updateThemeColor(e.matches)
  }
})

function updateThemeColor(isDark: boolean) {
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) {
    meta.setAttribute('content', isDark ? '#1E1E1E' : '#FFFFFF')
  }
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
