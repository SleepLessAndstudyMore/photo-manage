<template>
  <div id="photo-manager-app" :data-theme="theme">
    <!-- 移动端汉堡按钮 -->
    <button v-if="isMobile" class="mobile-menu-btn" @click="mobileNavOpen = !mobileNavOpen">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
    </button>
    <!-- 移动端遮罩 -->
    <div v-if="isMobile && mobileNavOpen" class="mobile-overlay" @click="mobileNavOpen = false" />
    <!-- 左侧导航栏 -->
    <nav class="app-nav" :class="{ 'is-open': mobileNavOpen }">
      <!-- 品牌 Logo -->
      <div class="nav-brand">
        <div class="brand-icon-wrapper">
          <svg class="brand-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
          </svg>
        </div>
        <span class="brand-name">PhotoVault</span>
        <span class="brand-dot" />
      </div>

      <div class="nav-links">
        <!-- 浏览分组 -->
        <div class="nav-group">
          <span class="nav-group-title">浏览</span>
          <router-link to="/timeline" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            <span class="nav-label">全部照片</span>
          </router-link>
          <router-link to="/folders" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="nav-label">文件夹</span>
          </router-link>
          <router-link to="/search" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <span class="nav-label">搜索</span>
          </router-link>
          <router-link to="/map" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
            </svg>
            <span class="nav-label">地图</span>
          </router-link>
        </div>

        <!-- 智能分类分组 -->
        <div class="nav-group">
          <span class="nav-group-title">智能分类</span>
          <router-link to="/people" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            <span class="nav-label">人物</span>
          </router-link>
          <router-link to="/tags" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>
            </svg>
            <span class="nav-label">标签</span>
          </router-link>
          <router-link to="/albums" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
            <span class="nav-label">相册</span>
          </router-link>
        </div>

        <!-- 工具分组 -->
        <div class="nav-group">
          <span class="nav-group-title">工具</span>
          <router-link to="/duplicates" class="nav-link" active-class="nav-link--active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            <span class="nav-label">清理</span>
          </router-link>
        </div>
      </div>

      <div class="nav-footer">
        <router-link to="/settings" class="nav-link" active-class="nav-link--active">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <span class="nav-label">设置</span>
        </router-link>
      </div>
    </nav>

    <!-- 内容区 -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '@/stores/system'

const theme = ref(localStorage.getItem('theme') || 'system')
const isMobile = ref(false)
const mobileNavOpen = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    mobileNavOpen.value = false
  }
}

onMounted(() => {
  useSystemStore().connectWs()
  applyTheme(theme.value)
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
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
/* ===== 全屏布局 ===== */
#photo-manager-app {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ===== 左侧导航栏 ===== */
.app-nav {
  width: 220px;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  padding: var(--space-4) var(--space-3);
  gap: var(--space-2);
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  flex-shrink: 0;
  z-index: 100;
}

/* ===== 品牌 Logo ===== */
.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
}

.brand-icon-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px var(--brand-glow);
}

.brand-icon {
  width: 18px;
  height: 18px;
}

.brand-name {
  font-size: var(--text-h3);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.brand-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand-gradient);
  margin-left: auto;
  flex-shrink: 0;
}

/* ===== 导航链接组 ===== */
.nav-links {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  overflow-y: auto;
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-group-title {
  font-size: 12px;
  font-weight: var(--font-weight-semibold);
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: var(--space-1) var(--space-3);
  margin-bottom: var(--space-1);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  height: 36px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  position: relative;
  cursor: pointer;
}

.nav-link:hover {
  background: #F9FAFB;
  color: var(--text-primary);
}

.nav-link:hover::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 20px;
  border-radius: 0 2px 2px 0;
  background: #E5E7EB;
}

.nav-link--active {
  color: #4F46E5;
  background: #EEF2FF;
  font-weight: var(--font-weight-semibold);
}

.nav-link--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 0 2px 2px 0;
  background: var(--brand-gradient);
}

.nav-link--active:hover {
  background: #EEF2FF;
}

.nav-link--active:hover::before {
  background: var(--brand-gradient);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  stroke-width: 1.5;
}

.nav-link--active .nav-icon {
  color: #6366F1;
}

.nav-label {
  white-space: nowrap;
}

/* ===== 底部设置 ===== */
.nav-footer {
  border-top: 1px solid var(--border-color);
  padding-top: var(--space-3);
  margin-top: auto;
}

/* ===== 内容区 ===== */
.app-main {
  flex: 1;
  overflow: hidden;
  background: transparent;
}

/* ===== 深色模式适配 ===== */
[data-theme="dark"] .nav-link:hover {
  background: rgba(255, 255, 255, 0.04);
}

[data-theme="dark"] .nav-link:hover::before {
  background: #475569;
}

[data-theme="dark"] .nav-link--active {
  background: rgba(129, 140, 248, 0.15);
  color: #818CF8;
}

[data-theme="dark"] .nav-link--active .nav-icon {
  color: #818CF8;
}

[data-theme="dark"] .nav-group-title {
  color: #94A3B8;
}

.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 200;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 90;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }

  .mobile-overlay {
    display: block;
  }

  .app-nav {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.3s var(--ease-standard);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
  }

  .app-nav.is-open {
    transform: translateX(0);
  }

  .app-main {
    padding-top: 56px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .app-nav {
    width: 64px;
    min-width: 64px;
    padding: var(--space-4) var(--space-2);
  }
  .nav-brand {
    justify-content: center;
    padding: var(--space-2) 0;
  }
  .brand-name {
    display: none;
  }
  .brand-dot {
    display: none;
  }
  .nav-group-title {
    display: none;
  }
  .nav-label {
    display: none;
  }
  .nav-link {
    justify-content: center;
    padding: var(--space-2) 0;
  }
  .nav-link--active::before {
    left: 0;
    width: 2px;
    height: 24px;
  }
}
</style>
