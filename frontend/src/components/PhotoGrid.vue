<template>
  <div ref="containerRef" class="photo-grid-container">
    <!-- 加载骨架屏 -->
    <div v-if="loading && photos.length === 0" class="loading-state">
      <div class="skeleton-grid">
        <div v-for="i in 8" :key="i" class="skeleton-card">
          <el-skeleton :rows="0" animated />
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <EmptyState
      v-else-if="!loading && photos.length === 0"
      type="photos"
      :title="emptyText || '暂无照片'"
      subtitle="将照片添加到图库源，精彩瞬间将在这里呈现"
    />

    <!-- 照片网格（按日期分组） -->
    <div v-else ref="scrollRef" class="photo-scroll-area" @scroll="onScroll">
      <div
        v-for="group in groupedPhotos"
        :key="group.date"
        class="photo-group"
      >
        <!-- 日期分组标题 -->
        <div class="group-header">
          <div class="group-accent-line" />
          <span class="group-date">{{ group.displayDate }}</span>
          <span class="group-count">{{ group.photos.length }} 张</span>
        </div>

        <!-- 照片网格 -->
        <div class="photo-grid">
          <div
            v-for="(photo, index) in group.photos"
            :key="photo.id"
            class="photo-card"
            :class="{
              'is-selected': selectedIds.has(photo.id),
              'is-favorite': photo.is_favorite,
              'is-other-selected': hasSelection && !selectedIds.has(photo.id),
            }"
            :style="{ animationDelay: `${Math.min(index * 30, 300)}ms` }"
            @click="onPhotoClick(photo, $event)"
          >
            <div class="photo-card-inner">
              <img
                v-if="photo.thumbnail_path"
                :src="`/thumbnails/${photo.thumbnail_path}`"
                :alt="photo.file_name"
                loading="lazy"
                class="thumbnail-img"
                :class="{ 'is-loaded': loadedImages.has(photo.id) }"
                @load="onImageLoad(photo.id)"
                @error="onImageError($event)"
              />
              <div v-else class="thumbnail-placeholder">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>

              <!-- 文件丢失遮罩 -->
              <div v-if="photo.file_missing" class="missing-overlay">
                <span>文件丢失</span>
              </div>

              <!-- Hover 时浮现的收藏星标 -->
              <button
                v-if="!photo.file_missing"
                class="favorite-star"
                :class="{ 'is-fav': photo.is_favorite }"
                @click.stop="toggleFavorite(photo)"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" :fill="photo.is_favorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </button>

              <!-- 底部渐变遮罩 + 文件名 -->
              <div class="photo-overlay">
                <span class="photo-name">{{ photo.file_name }}</span>
              </div>

              <!-- 选中态对勾 -->
              <div v-if="selectedIds.has(photo.id)" class="check-badge">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="loading" class="loading-more">
        <div class="loading-spinner" />
        <span>加载中...</span>
      </div>
      <div ref="sentinelRef" class="scroll-sentinel" />
    </div>

    <!-- 批量操作栏 -->
    <Transition name="slide-up">
      <div v-if="selectedIds.size > 0" class="batch-action-bar">
        <div class="batch-info">
          <span class="batch-count">{{ selectedIds.size }} 张已选择</span>
        </div>
        <div class="batch-actions">
          <button class="batch-btn" @click="batchFavorite">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            收藏
          </button>
          <button class="batch-btn" @click="clearSelection">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            取消
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Photo } from '@/types/photo'
import EmptyState from './EmptyState.vue'

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
  'toggle-favorite': [photoId: number, isFavorite: boolean]
}>()

// === 图片加载状态 ===
const loadedImages = ref<Set<number>>(new Set())

function onImageLoad(photoId: number) {
  requestAnimationFrame(() => {
    loadedImages.value.add(photoId)
  })
}

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

// === 日期分组 ===
const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

interface PhotoGroup {
  date: string
  displayDate: string
  photos: Photo[]
}

const groupedPhotos = computed<PhotoGroup[]>(() => {
  const groups = new Map<string, Photo[]>()

  props.photos.forEach(photo => {
    const date = photo.date_taken ? photo.date_taken.split('T')[0] : '未知日期'
    if (!groups.has(date)) {
      groups.set(date, [])
    }
    groups.get(date)!.push(photo)
  })

  // 按日期降序排序
  const sortedDates = Array.from(groups.keys()).sort((a, b) => {
    if (a === '未知日期') return 1
    if (b === '未知日期') return -1
    return b.localeCompare(a)
  })

  return sortedDates.map(date => ({
    date,
    displayDate: formatDateHeader(date),
    photos: groups.get(date)!,
  }))
})

function formatDateHeader(dateStr: string): string {
  if (dateStr === '未知日期') return '未知日期'
  const d = new Date(dateStr + 'T00:00:00')
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const isToday = d.toDateString() === today.toDateString()
  const isYesterday = d.toDateString() === yesterday.toDateString()

  if (isToday) return `今天 · ${weekdays[d.getDay()]}`
  if (isYesterday) return `昨天 · ${weekdays[d.getDay()]}`

  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 · ${weekdays[d.getDay()]}`
}

// === 选中态 ===
const selectedIds = ref<Set<number>>(new Set())
const hasSelection = computed(() => selectedIds.value.size > 0)

function onPhotoClick(photo: Photo, event: MouseEvent) {
  if (event.ctrlKey || event.metaKey) {
    // Ctrl/Cmd + 点击 = 多选切换
    if (selectedIds.value.has(photo.id)) {
      selectedIds.value.delete(photo.id)
    } else {
      selectedIds.value.add(photo.id)
    }
    selectedIds.value = new Set(selectedIds.value)
  } else if (event.shiftKey && selectedIds.value.size > 0) {
    // Shift + 点击 = 范围选择（简化版：直接点击进入详情）
    emit('photo-click', photo)
  } else if (selectedIds.value.size > 0) {
    // 已有选中时单击 = 切换选中
    if (selectedIds.value.has(photo.id) && selectedIds.value.size === 1) {
      selectedIds.value.clear()
    } else {
      selectedIds.value.clear()
      selectedIds.value.add(photo.id)
    }
    selectedIds.value = new Set(selectedIds.value)
  } else {
    // 无选中时单击 = 进入详情
    emit('photo-click', photo)
  }
}

function clearSelection() {
  selectedIds.value.clear()
  selectedIds.value = new Set()
}

function toggleFavorite(photo: Photo) {
  emit('toggle-favorite', photo.id, !photo.is_favorite)
}

function batchFavorite() {
  // 批量收藏
  selectedIds.value.forEach(id => {
    emit('toggle-favorite', id, true)
  })
  clearSelection()
}

// === 无限滚动 ===
const containerRef = ref<HTMLElement | null>(null)
const scrollRef = ref<HTMLElement | null>(null)
const sentinelRef = ref<HTMLElement | null>(null)

let resizeObserver: ResizeObserver | null = null
let intersectionObserver: IntersectionObserver | null = null

onMounted(() => {
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

/* ===== 日期分组 ===== */
.photo-group {
  margin-bottom: var(--space-6);
}

.photo-group:last-child {
  margin-bottom: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  padding-left: var(--space-1);
}

.group-accent-line {
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: var(--brand-gradient);
  flex-shrink: 0;
}

.group-date {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.group-count {
  font-size: 12px;
  color: var(--text-placeholder);
  margin-left: var(--space-1);
  font-variant-numeric: tabular-nums;
}

/* ===== 照片网格 ===== */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 4px;
}

/* ===== 照片卡片 ===== */
.photo-card {
  border-radius: var(--radius-md);
  cursor: pointer;
  position: relative;
  aspect-ratio: 1;
  animation: stagger-in 0.35s var(--ease-standard) backwards;
  transition: transform 0.2s var(--ease-standard),
              box-shadow 0.2s var(--ease-standard);
  overflow: hidden;
}

[data-theme="dark"] .photo-card .photo-card-inner {
  border: 1px solid #334155;
}

.photo-card:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 10;
}

.photo-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: blur(20px);
  transform: scale(1.05);
  transition: filter 400ms var(--ease-standard),
              transform 400ms var(--ease-standard);
}

.thumbnail-img.is-loaded {
  filter: blur(0px);
  transform: scale(1);
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

/* 文件丢失遮罩 */
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

/* ===== Hover 收藏星标 ===== */
.favorite-star {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transform: scale(0.8);
  transition: opacity 0.2s var(--ease-standard),
              transform 0.2s var(--ease-standard),
              background 0.2s var(--ease-standard);
  cursor: pointer;
  z-index: 5;
}

.photo-card:hover .favorite-star {
  opacity: 1;
  transform: scale(1);
}

.favorite-star:hover {
  background: rgba(0, 0, 0, 0.6);
}

.favorite-star.is-fav {
  color: #FFD60A;
  opacity: 1;
  transform: scale(1);
}

/* ===== 底部渐变遮罩 ===== */
.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 28px 8px 8px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));
  opacity: 0;
  transition: opacity 0.2s var(--ease-standard);
  pointer-events: none;
  z-index: 3;
}

.photo-card:hover .photo-overlay {
  opacity: 1;
}

.photo-name {
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

/* ===== 选中态 ===== */
.photo-card.is-selected .photo-card-inner {
  transform: scale(0.95);
  box-shadow: 0 0 0 2px var(--accent);
}

.photo-card.is-selected::after {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'/%3E%3C/svg%3E");
  background-size: 14px;
  background-position: center;
  background-repeat: no-repeat;
  box-shadow: 0 2px 8px var(--brand-glow);
  z-index: 10;
}

/* 其他照片未选中时的轻微遮罩 */
.photo-card.is-other-selected .photo-card-inner::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.08);
  pointer-events: none;
  z-index: 2;
}

.check-badge {
  display: none;
}

/* ===== 骨架屏 ===== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 4px;
  padding: var(--space-4);
}

.skeleton-card {
  aspect-ratio: 1;
  border-radius: var(--radius-md);
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
  gap: var(--space-3);
  color: var(--text-placeholder);
}

.empty-illustration svg {
  width: 160px;
  height: 120px;
}

.empty-text {
  font-size: var(--text-h3);
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

.empty-subtitle {
  font-size: var(--text-body);
  color: var(--text-tertiary);
  margin: 0;
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

.scroll-sentinel {
  height: 1px;
}

/* ===== 批量操作栏 ===== */
.batch-action-bar {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 100;
  backdrop-filter: blur(12px);
}

.batch-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.batch-count {
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.batch-actions {
  display: flex;
  gap: var(--space-2);
}

.batch-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-caption);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.batch-btn:hover {
  background: var(--gray-100);
  color: var(--text-primary);
}

[data-theme="dark"] .batch-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

[data-theme="dark"] .thumbnail-placeholder {
  background: var(--gray-800);
}

[data-theme="dark"] .photo-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .skeleton-card {
  background: var(--gray-800);
}
</style>
