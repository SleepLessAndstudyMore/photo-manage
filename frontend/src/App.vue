<template>
  <div id="photo-manager-app" :data-theme="theme">
    <nav class="app-nav">
      <div class="nav-logo">
        <span class="nav-logo-icon">&#x1F4F7;</span>
        <span class="nav-logo-text">PhotoManager</span>
      </div>
      <div class="nav-links">
        <router-link to="/timeline" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          <span class="nav-label">时间轴</span>
        </router-link>
        <router-link to="/folders" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span class="nav-label">文件夹</span>
        </router-link>
        <router-link to="/search" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <span class="nav-label">搜索</span>
        </router-link>
        <router-link to="/tags" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>
          </svg>
          <span class="nav-label">标签</span>
        </router-link>
        <router-link to="/albums" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>
          </svg>
          <span class="nav-label">相册</span>
        </router-link>
        <router-link to="/map" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          <span class="nav-label">地图</span>
        </router-link>
        <router-link to="/people" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
          </svg>
          <span class="nav-label">人物</span>
        </router-link>
        <router-link to="/duplicates" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span class="nav-label">清理</span>
        </router-link>
      </div>
      <div class="nav-footer">
        <router-link to="/settings" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <span class="nav-label">设置</span>
        </router-link>
      </div>
    </nav>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'

const theme = ref(localStorage.getItem('theme') || 'system')

onMounted(() => {
  useSystemStore().connectWs()
  applyTheme(theme.value)
})

function applyTheme(t: string) {
  const isDark = t === 'dark' || (t === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  if (isDark) {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
  // Update theme-color meta
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) {
    meta.setAttribute('content', isDark ? '#1E1E1E' : '#FFFFFF')
  }
}

// Expose for settings page
if (typeof window !== 'undefined') {
  ;(window as any).__setTheme = (t: string) => {
    theme.value = t
    applyTheme(t)
  }
}
</script>

<style>
/* ===== 左侧导航栏 — visionOS 风格 ===== */
#photo-manager-app {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
  transition: background var(--transition-normal);
}

.app-nav {
  width: 200px;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  padding: var(--space-md) var(--space-sm);
  gap: var(--space-xs);
  border-right: 1px solid var(--border-color);
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  flex-shrink: 0;
  z-index: 100;
  transition: background var(--transition-normal), border-color var(--transition-normal);
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.5);
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-md);
}

.nav-logo-icon {
  font-size: 22px;
  line-height: 1;
}

.nav-logo-text {
  font-family: var(--font-display);
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

.nav-links {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-footer {
  border-top: 1px solid var(--border-color);
  padding-top: var(--space-sm);
  margin-top: auto;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px var(--space-md);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
}

.nav-link:hover {
  background: var(--accent-light);
  color: var(--text-primary);
}

.nav-link--active {
  color: var(--accent);
  background: var(--accent-light);
  font-weight: 600;
}

.nav-link--active::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  border-radius: 2px;
  background: var(--accent);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
}

.app-main {
  flex: 1;
  overflow: hidden;
  background: transparent;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .app-nav {
    width: 60px;
    min-width: 60px;
  }
  .nav-logo-text,
  .nav-label {
    display: none;
  }
  .nav-logo {
    justify-content: center;
    padding: var(--space-sm) 0;
  }
  .nav-link {
    justify-content: center;
    padding: 10px 0;
  }
  .nav-link--active::before {
    left: 0;
    width: 2px;
    height: 24px;
  }
}
</style>
