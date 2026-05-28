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
          <rect x="20" y="30" width="80" height="60" rx="12" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.2"/>
          <circle cx="55" cy="58" r="10" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.2"/>
          <path d="M30 78l15-15 10 10 15-20 20 25" stroke="currentColor" stroke-width="1.5" opacity="0.2"/>
        </svg>
      </div>
      <p class="empty-text">{{ emptyText || '暂无照片' }}</p>
    </div>
    <div v-else ref="scrollRef" class="photo-scroll-area" @scroll="onScroll">
      <div class="photo-grid">
        <div
          v-for="(photo, index) in photos"
          :key="photo.id"
          class="photo-card"
          :style="{ animationDelay: `${Math.min(index * 30, 300)}ms` }"
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
const GAP = 4

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

function onScroll() {}

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.photo-grid-container {
  height: 100%;
  position: relative;
}

.photo-scroll-area {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-4);
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-1);
}

/* ===== 照片卡片 ===== */
.photo-card {
  border-radius: var(--radius-sm);
  cursor: pointer;
  position: relative;
  aspect-ratio: 1;
  animation: stagger-in 0.4s var(--transition-normal) backwards;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.photo-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15), 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.photo-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  background: var(--gray-100);
}


.missing-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(128, 128, 128, 0.7);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: var(--text-caption);
  font-weight: var(--font-weight-semibold);
}

.favorite-badge {
  position: absolute;
  top: var(--space-1);
  right: var(--space-1);
  color: #FFD60A;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.4));
}

/* ===== 骨架屏 ===== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-1);
}

.skeleton-card {
  aspect-ratio: 1;
  border-radius: var(--radius-xs);
  overflow: hidden;
  background: var(--gray-100);
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--space-4);
  color: var(--text-placeholder);
}

.empty-illustration svg {
  width: 120px;
  height: 120px;
  color: var(--gray-300);
}

.empty-text {
  font-size: var(--text-h3);
  color: var(--text-secondary);
  font-weight: var(--font-weight-regular);
}

/* ===== 加载更多 ===== */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-6);
  color: var(--text-secondary);
  font-size: var(--text-caption);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--gray-200);
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
