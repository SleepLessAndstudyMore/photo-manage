<template>
  <div id="photo-manager-app" :data-theme="theme">
    <!-- macOS 窗口外壳 -->
    <div class="window-shell">
      <!-- 窗口标题栏 -->
      <header class="window-titlebar">
        <div class="traffic-lights">
          <span class="tl-btn tl-close" />
          <span class="tl-btn tl-minimize" />
          <span class="tl-btn tl-maximize" />
        </div>
        <span class="window-title">PhotoManager</span>
        <div class="titlebar-spacer" />
      </header>

      <!-- 窗口内容区 -->
      <div class="window-body">
        <!-- 左侧导航栏 -->
        <nav class="app-nav">
          <div class="nav-links">
            <router-link to="/timeline" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              <span class="nav-label">时间轴</span>
            </router-link>
            <router-link to="/folders" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
              </svg>
              <span class="nav-label">文件夹</span>
            </router-link>
            <router-link to="/search" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <span class="nav-label">搜索</span>
            </router-link>
            <router-link to="/tags" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
              <span class="nav-label">标签</span>
            </router-link>
            <router-link to="/albums" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" />
              </svg>
              <span class="nav-label">相册</span>
            </router-link>
            <router-link to="/map" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" />
              </svg>
              <span class="nav-label">地图</span>
            </router-link>
            <router-link to="/people" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
              </svg>
              <span class="nav-label">人物</span>
            </router-link>
            <router-link to="/duplicates" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
              <span class="nav-label">清理</span>
            </router-link>
          </div>
          <div class="nav-footer">
            <router-link to="/settings" class="nav-link" active-class="nav-link--active">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
              <span class="nav-label">设置</span>
            </router-link>
          </div>
        </nav>

        <!-- 内容区 -->
        <main class="app-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
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
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) {
    meta.setAttribute('content', isDark ? '#111114' : '#f5f7fb')
  }
}

if (typeof window !== 'undefined') {
  ;(window as any).__setTheme = (t: string) => {
    theme.value = t
    applyTheme(t)
  }
}
</script>

<style>
/* ===== macOS 窗口外壳 ===== */
#photo-manager-app {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  padding: 12px;
  background: transparent;
}

.window-shell {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  border-radius: var(--window-radius);
  overflow: hidden;
  box-shadow: var(--window-shadow);
  background: var(--card-bg);
  backdrop-filter: blur(60px);
  -webkit-backdrop-filter: blur(60px);
  border: 1px solid var(--border-glass);
}

/* ===== 窗口标题栏 ===== */
.window-titlebar {
  display: flex;
  align-items: center;
  padding: 0 var(--space-lg);
  height: 44px;
  background: rgba(245, 247, 251, 0.65);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  -webkit-app-region: drag;
}

[data-theme="dark"] .window-titlebar {
  background: rgba(30, 30, 34, 0.5);
}

.traffic-lights {
  display: flex;
  gap: 8px;
  -webkit-app-region: no-drag;
}

.tl-btn {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tl-close {
  background: #FF5F57;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08);
}
.tl-minimize {
  background: #FEBC2E;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08);
}
.tl-maximize {
  background: #28C840;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08);
}

.window-title {
  flex: 1;
  text-align: center;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: -0.2px;
}

.titlebar-spacer {
  width: 52px;
}

/* ===== 窗口内容区 ===== */
.window-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ===== 左侧导航栏 — 悬浮毛玻璃 ===== */
.app-nav {
  width: 200px;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  padding: var(--space-md) var(--space-sm);
  gap: 2px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid var(--border-color);
  flex-shrink: 0;
  z-index: 100;
  transition: background var(--transition-normal);
}

[data-theme="dark"] .app-nav {
  background: rgba(255, 255, 255, 0.04);
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
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
  letter-spacing: -0.1px;
}

.nav-link:hover {
  background: var(--accent-light);
  color: var(--text-primary);
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.06);
}

.nav-link--active {
  color: var(--accent);
  background: var(--accent-light);
  font-weight: 600;
  box-shadow: 0 0 20px var(--accent-glow);
}

.nav-link--active::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  border-radius: 2px;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent-glow);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  transition: transform var(--transition-fast);
}

.nav-link:hover .nav-icon {
  transform: scale(1.06);
}

.nav-label {
  white-space: nowrap;
}

/* ===== 内容区 ===== */
.app-main {
  flex: 1;
  overflow: hidden;
  background: transparent;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  #photo-manager-app {
    padding: 0;
  }
  .window-shell {
    border-radius: 0;
  }
  .window-titlebar {
    display: none;
  }
  .app-nav {
    width: 60px;
    min-width: 60px;
  }
  .nav-label {
    display: none;
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
