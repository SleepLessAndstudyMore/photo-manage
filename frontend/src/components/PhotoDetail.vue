<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="lightbox-overlay" @click.self="$emit('close')">
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
        <div class="lightbox-content">
          <img
            v-if="currentPhoto"
            :src="previewSrc"
            :alt="currentPhoto.file_name"
            class="lightbox-img"
            @click.stop
          />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
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
}

.lightbox-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 6px;
  user-select: none;
  box-shadow: 0 20px 80px rgba(0, 0, 0, 0.5);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
