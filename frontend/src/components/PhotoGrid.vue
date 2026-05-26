<template>
  <div ref="containerRef" class="photo-grid-container">
    <div v-if="loading && photos.length === 0" class="loading-state">
      <div class="skeleton-grid">
        <div v-for="i in 8" :key="i" class="skeleton-card">
          <el-skeleton :rows="0" animated />
        </div>
      </div>
    </div>
    <div v-else-if="!loading && photos.length === 0" class="empty-state">
      <div class="empty-illustration">
        <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="30" width="80" height="60" rx="8" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
          <circle cx="55" cy="58" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
          <path d="M30 78l15-15 10 10 15-20 20 25" stroke="currentColor" stroke-width="2" opacity="0.3"/>
        </svg>
      </div>
      <p class="empty-text">{{ emptyText || '暂无照片' }}</p>
    </div>
    <div v-else ref="scrollRef" class="photo-scroll-area" @scroll="onScroll">
      <div class="photo-grid">
        <div
          v-for="photo in photos"
          :key="photo.id"
          class="photo-card"
          @click="$emit('photo-click', photo)"
        >
          <div class="photo-card-inner">
            <img
              v-if="photo.thumbnail_path"
              :src="`/thumbnails/${photo.thumbnail_path}`"
              :alt="photo.file_name"
              loading="lazy"
              class="thumbnail-img"
              @error="onImageError($event)"
            />
            <div v-else class="thumbnail-placeholder">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <div v-if="photo.is_video" class="video-overlay">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              <span v-if="photo.duration" class="duration-label">{{ formatDuration(photo.duration) }}</span>
            </div>
            <div v-if="photo.file_missing" class="missing-overlay">
              <span>文件丢失</span>
            </div>
            <div v-if="photo.is_favorite" class="favorite-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
      <div v-if="loading" class="loading-more">
        <div class="loading-spinner" />
        <span>加载中...</span>
      </div>
      <div ref="sentinelRef" class="scroll-sentinel" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { Photo } from '@/types/photo'

const props = withDefaults(defineProps<{
  photos: Photo[]
  loading?: boolean
  emptyText?: string
}>(), {
  loading: false,
  emptyText: '暂无照片',
})

const emit = defineEmits<{
  'photo-click': [photo: Photo]
  'load-more': []
}>()

const containerRef = ref<HTMLElement | null>(null)
const scrollRef = ref<HTMLElement | null>(null)
const sentinelRef = ref<HTMLElement | null>(null)
const columns = ref(4)
const MIN_COL_WIDTH = 220
const GAP = 16

function updateColumns() {
  if (!containerRef.value) return
  const w = containerRef.value.clientWidth
  columns.value = Math.max(1, Math.floor((w + GAP) / (MIN_COL_WIDTH + GAP)))
}

let resizeObserver: ResizeObserver | null = null
let intersectionObserver: IntersectionObserver | null = null

onMounted(() => {
  updateColumns()
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(updateColumns)
    resizeObserver.observe(containerRef.value)
  }
  if (sentinelRef.value) {
    intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          emit('load-more')
        }
      },
      { root: scrollRef.value, rootMargin: '200px' }
    )
    intersectionObserver.observe(sentinelRef.value)
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  intersectionObserver?.disconnect()
})

function onScroll() {
  // Handled by IntersectionObserver
}

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.photo-grid-container {
  height: 100%;
  overflow: hidden;
  position: relative;
}

.photo-scroll-area {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-md);
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-md);
}

/* ===== 照片卡片 — 毛玻璃悬浮卡片 ===== */
.photo-card {
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--card-shadow);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  aspect-ratio: 1;
}

.photo-card:hover {
  transform: scale(1.02);
  box-shadow: var(--card-shadow-hover);
}

.photo-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.photo-card:hover .thumbnail-img {
  transform: scale(1.05);
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  background: var(--bg-secondary);
}

.video-overlay {
  position: absolute;
  bottom: var(--space-sm);
  left: var(--space-sm);
  display: flex;
  align-items: center;
  gap: 4px;
  color: #fff;
  background: rgba(0, 0, 0, 0.6);
  padding: 3px 10px;
  border-radius: 100px;
  font-size: var(--text-xs);
  backdrop-filter: blur(8px);
}

.duration-label {
  font-size: var(--text-xs);
}

.missing-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(128, 128, 128, 0.7);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.favorite-badge {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  color: #f5a623;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.4));
}

/* ===== 骨架屏 ===== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-md);
}

.skeleton-card {
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-secondary);
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--space-md);
  color: var(--text-tertiary);
}

.empty-illustration svg {
  width: 100px;
  height: 100px;
  color: var(--text-tertiary);
}

.empty-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
}

/* ===== 加载更多 ===== */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-lg);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.scroll-sentinel {
  height: 1px;
}
</style>
