<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="lightbox-overlay" @click.self="onOverlayClick">
        <div class="lightbox-toolbar">
          <button class="pill-btn lightbox-btn" @click="$emit('prev')">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <span class="lightbox-counter">{{ currentIndex + 1 }} / {{ photos.length }}</span>
          <button class="pill-btn lightbox-btn" @click="$emit('next')">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
          <div class="lightbox-actions">
            <button class="pill-btn lightbox-btn" @click="resetTransform" title="重置">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
              </svg>
            </button>
            <button
              class="pill-btn lightbox-btn"
              :class="{ 'is-fav': currentPhoto?.is_favorite }"
              @click.stop="toggleFavorite"
            >
              <svg v-if="currentPhoto?.is_favorite" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </button>
            <button class="pill-btn lightbox-btn" @click="$emit('close')">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <div
          class="lightbox-content"
          @wheel.prevent="onWheel"
          @mousedown.prevent="onMouseDown"
          @mousemove="onMouseMove"
          @mouseup="onMouseUp"
          @mouseleave="onMouseUp"
          @dblclick="onDoubleClick"
          ref="contentRef"
        >
          <img
            v-if="currentPhoto"
            :src="previewSrc"
            :alt="currentPhoto.file_name"
            class="lightbox-img"
            :style="imageStyle"
            draggable="false"
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Photo } from '@/types/photo'

const props = defineProps<{
  photos: Photo[]
  currentIndex: number
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
  prev: []
  next: []
  'update:favorite': [photoId: number, isFavorite: boolean]
}>()

const currentPhoto = computed(() => props.photos[props.currentIndex] ?? null)

const previewSrc = computed(() => {
  if (!currentPhoto.value) return ''
  if (!currentPhoto.value.file_missing) {
    return `/api/v1/photos/${currentPhoto.value.id}/original`
  }
  if (currentPhoto.value.preview_path) {
    return `/thumbnails/${currentPhoto.value.preview_path}`
  }
  if (currentPhoto.value.thumbnail_path) {
    return `/thumbnails/${currentPhoto.value.thumbnail_path}`
  }
  return ''
})

function toggleFavorite() {
  if (currentPhoto.value) {
    emit('update:favorite', currentPhoto.value.id, !currentPhoto.value.is_favorite)
  }
}

// === 缩放与拖拽状态 ===
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartTranslateX = ref(0)
const dragStartTranslateY = ref(0)
const hasDragged = ref(false)
const contentRef = ref<HTMLElement | null>(null)

const imageStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
  cursor: isDragging.value ? 'grabbing' : scale.value > 1 ? 'grab' : 'default',
}))

function resetTransform() {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

watch(() => props.currentIndex, resetTransform)

function onWheel(e: WheelEvent) {
  const delta = e.deltaY < 0 ? 1.1 : 0.9
  const newScale = Math.max(0.5, Math.min(5, scale.value * delta))

  if (newScale === scale.value) return

  // 以鼠标位置为中心缩放
  const rect = contentRef.value?.getBoundingClientRect()
  if (!rect) {
    scale.value = newScale
    return
  }

  const mouseX = e.clientX - rect.left - rect.width / 2
  const mouseY = e.clientY - rect.top - rect.height / 2

  const scaleRatio = newScale / scale.value
  translateX.value = mouseX - (mouseX - translateX.value) * scaleRatio
  translateY.value = mouseY - (mouseY - translateY.value) * scaleRatio
  scale.value = newScale

  if (scale.value <= 1) {
    translateX.value = 0
    translateY.value = 0
  }
}

function onMouseDown(e: MouseEvent) {
  if (e.button !== 0) return
  isDragging.value = true
  hasDragged.value = false
  dragStartX.value = e.clientX
  dragStartY.value = e.clientY
  dragStartTranslateX.value = translateX.value
  dragStartTranslateY.value = translateY.value
}

function onMouseMove(e: MouseEvent) {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartX.value
  const dy = e.clientY - dragStartY.value

  if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
    hasDragged.value = true
  }

  translateX.value = dragStartTranslateX.value + dx
  translateY.value = dragStartTranslateY.value + dy
}

function onMouseUp() {
  isDragging.value = false
}

function onOverlayClick() {
  // 如果正在拖拽中，忽略点击
  if (hasDragged.value) return
  emit('close')
}

function onDoubleClick() {
  if (scale.value > 1) {
    resetTransform()
  } else {
    scale.value = 2
  }
}
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.lightbox-toolbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 var(--space-lg);
  color: #fff;
  z-index: 10;
  gap: var(--space-sm);
}

.lightbox-btn {
  color: #fff !important;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  padding: 8px 12px;
  border: none;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.lightbox-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.lightbox-btn.is-fav {
  color: #f5a623 !important;
}

.lightbox-counter {
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.7);
  user-select: none;
  min-width: 60px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.lightbox-actions {
  margin-left: auto;
  display: flex;
  gap: var(--space-xs);
}

.lightbox-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 80px 60px 60px;
  box-sizing: border-box;
  overflow: hidden;
}

.lightbox-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 6px;
  user-select: none;
  box-shadow: 0 20px 80px rgba(0, 0, 0, 0.5);
  transition: transform 0.1s ease-out;
  will-change: transform;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
