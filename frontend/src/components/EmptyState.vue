<template>
  <div class="empty-state">
    <!-- 品牌渐变插画 -->
    <div class="empty-illustration">
      <svg viewBox="0 0 160 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="emptyGrad" x1="0" y1="0" x2="160" y2="120" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#6366F1" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0.12"/>
          </linearGradient>
          <linearGradient id="emptyAccent" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#6366F1"/>
            <stop offset="100%" stop-color="#8B5CF6"/>
          </linearGradient>
        </defs>

        <!-- 背景 -->
        <rect x="30" y="15" width="100" height="90" rx="16" fill="url(#emptyGrad)"/>

        <!-- 插画内容根据 type 变化 -->
        <g v-if="type === 'photos'">
          <rect x="50" y="35" width="60" height="50" rx="8" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <circle cx="68" cy="55" r="8" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <path d="M55 78l12-12 8 8 12-16 18 20" stroke="url(#emptyAccent)" stroke-width="1.5" opacity="0.4"/>
        </g>

        <g v-else-if="type === 'albums'">
          <rect x="50" y="40" width="60" height="45" rx="6" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <line x1="50" y1="52" x2="110" y2="52" stroke="url(#emptyAccent)" stroke-width="1.5" opacity="0.3"/>
          <rect x="60" y="60" width="14" height="14" rx="2" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
          <rect x="80" y="60" width="14" height="14" rx="2" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
        </g>

        <g v-else-if="type === 'tags'">
          <path d="M60 40l-15 15v20h30v-20z" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <circle cx="60" cy="55" r="4" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <rect x="85" y="48" width="20" height="10" rx="5" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
          <rect x="85" y="62" width="16" height="8" rx="4" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.2"/>
        </g>

        <g v-else-if="type === 'people'">
          <circle cx="72" cy="48" r="14" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <path d="M52 78c0-11 9-20 20-20s20 9 20 20" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <circle cx="100" cy="58" r="6" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
        </g>

        <g v-else-if="type === 'search'">
          <circle cx="68" cy="55" r="16" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <line x1="80" y1="67" x2="95" y2="82" stroke="url(#emptyAccent)" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
          <rect x="95" y="38" width="12" height="8" rx="2" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.2" transform="rotate(15 101 42)"/>
        </g>

        <g v-else-if="type === 'map'">
          <path d="M50 40l10-8 20 6 20-4v50l-20 4-20-6-10 8z" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <path d="M60 32v50M80 38v50M100 36v50" stroke="url(#emptyAccent)" stroke-width="0.75" opacity="0.2"/>
          <circle cx="72" cy="58" r="5" fill="url(#emptyAccent)" opacity="0.4"/>
        </g>

        <g v-else-if="type === 'clean'">
          <rect x="55" y="45" width="50" height="38" rx="6" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <polyline points="62 60 70 68 85 53 98 66" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.4"/>
          <circle cx="95" cy="42" r="8" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
        </g>

        <g v-else-if="type === 'folder'">
          <path d="M55 48l6-8h20l6 8h18v30H55z" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <rect x="60" y="58" width="12" height="10" rx="2" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
          <rect x="78" y="58" width="12" height="10" rx="2" stroke="url(#emptyAccent)" stroke-width="1" fill="none" opacity="0.3"/>
        </g>

        <!-- 默认插画 -->
        <g v-else>
          <rect x="50" y="35" width="60" height="50" rx="8" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <circle cx="68" cy="55" r="8" stroke="url(#emptyAccent)" stroke-width="1.5" fill="none" opacity="0.4"/>
          <path d="M55 78l12-12 8 8 12-16 18 20" stroke="url(#emptyAccent)" stroke-width="1.5" opacity="0.4"/>
        </g>
      </svg>
    </div>

    <!-- 文案 -->
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="subtitle" class="empty-subtitle">{{ subtitle }}</p>

    <!-- 操作按钮 -->
    <div v-if="$slots.action || actionText" class="empty-action">
      <slot name="action">
        <button v-if="actionText" class="empty-btn" @click="$emit('action')">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          {{ actionText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  type?: 'photos' | 'albums' | 'tags' | 'people' | 'search' | 'map' | 'clean' | 'folder' | string
  title: string
  subtitle?: string
  actionText?: string
  actionIcon?: boolean
}>()

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--space-3);
  color: var(--text-placeholder);
  padding: var(--space-8);
}

.empty-illustration {
  filter: drop-shadow(0 8px 16px var(--brand-glow));
}

.empty-illustration svg {
  width: 160px;
  height: 120px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  margin-top: var(--space-2);
}

.empty-subtitle {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-tertiary);
  margin: 0;
  text-align: center;
  max-width: 320px;
  line-height: 1.6;
}

.empty-action {
  margin-top: var(--space-4);
}

.empty-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 10px 24px;
  border-radius: 100px;
  border: none;
  background: var(--brand-gradient);
  color: white;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: all 200ms var(--ease-standard);
  box-shadow: 0 4px 14px var(--brand-glow), 0 1px 3px rgba(0,0,0,0.1);
}

.empty-btn:hover {
  background: var(--brand-gradient-hover);
  box-shadow: 0 8px 24px var(--brand-glow-strong), 0 2px 6px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.empty-btn:active {
  transform: scale(0.96) translateY(0);
}

[data-theme="dark"] .empty-illustration {
  filter: drop-shadow(0 8px 16px rgba(129, 140, 248, 0.15));
}
</style>
