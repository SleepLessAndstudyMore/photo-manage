<template>
  <div ref="containerRef" class="photo-grid-container">
    <div v-if="loading && photos.length === 0" class="loading-state">
      <el-skeleton :rows="3" animated />
      <el-skeleton :rows="3" animated style="margin-top: 16px" />
    </div>
    <div v-else-if="!loading && photos.length === 0" class="empty-state">
      <el-empty :description="emptyText || '暂无照片'" />
    </div>
    <div v-else ref="scrollRef" class="photo-scroll-area" @scroll="onScroll">
      <div class="photo-grid" :style="{ width: '100%' }">
        <div
          v-for="photo in photos"
          :key="photo.id"
          class="photo-card"
          :style="cardStyle(photo)"
          @click="$emit('photo-click', photo)"
        >
          <img
            v-if="photo.thumbnail_path"
            :src="`/thumbnails/${photo.thumbnail_path}`"
            :alt="photo.file_name"
            loading="lazy"
            class="thumbnail-img"
            @error="onImageError($event)"
          />
          <div v-else class="thumbnail-placeholder">
            <el-icon :size="28"><PictureFilled /></el-icon>
          </div>
          <div v-if="photo.is_video" class="video-overlay">
            <el-icon :size="20"><VideoPlay /></el-icon>
            <span v-if="photo.duration" class="duration-label">{{ formatDuration(photo.duration) }}</span>
          </div>
          <div v-if="photo.file_missing" class="missing-overlay">
            <span>文件丢失</span>
          </div>
          <div v-if="photo.is_favorite" class="favorite-badge">
            <el-icon :size="14"><StarFilled /></el-icon>
          </div>
        </div>
      </div>
      <div v-if="loading" class="loading-more">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div ref="sentinelRef" class="scroll-sentinel" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Loading, PictureFilled, VideoPlay, StarFilled } from '@element-plus/icons-vue'
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
const MIN_COL_WIDTH = 200
const GAP = 8

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

const colWidth = computed(() => {
  if (!containerRef.value) return MIN_COL_WIDTH
  const w = containerRef.value.clientWidth
  return Math.floor((w - (columns.value - 1) * GAP) / columns.value)
})

function cardStyle(photo: Photo) {
  const aspect = (photo.thumbnail_width && photo.thumbnail_height)
    ? photo.thumbnail_width / photo.thumbnail_height
    : (photo.width && photo.height ? photo.width / photo.height : 1.5)
  const h = Math.round(colWidth.value / Math.max(aspect, 0.3))
  return { width: colWidth.value + 'px', height: h + 'px' }
}

function onScroll() {
  // Handled by IntersectionObserver
}

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  img.parentElement?.classList.add('has-error')
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
  padding: 8px;
}
.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.photo-card {
  position: relative;
  overflow: hidden;
  border-radius: 6px;
  cursor: pointer;
  background: var(--color-bg-secondary, #f0f0f0);
  flex-shrink: 0;
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
  color: var(--color-text-tertiary, #bbb);
}
.video-overlay {
  position: absolute;
  bottom: 6px;
  left: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #fff;
  background: rgba(0,0,0,0.6);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.duration-label {
  font-size: 11px;
}
.missing-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(128, 128, 128, 0.7);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}
.favorite-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  color: #f5a623;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.4));
}
.loading-state, .empty-state {
  padding: 40px;
  text-align: center;
}
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: var(--color-text-secondary, #999);
  font-size: 13px;
}
.scroll-sentinel {
  height: 1px;
}
</style>
