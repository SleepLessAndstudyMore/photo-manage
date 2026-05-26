<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="lightbox-overlay" @click.self="$emit('close')">
        <div class="lightbox-toolbar">
          <el-button text :icon="ArrowLeft" circle @click="$emit('prev')" />
          <span class="lightbox-counter">{{ currentIndex + 1 }} / {{ photos.length }}</span>
          <el-button text :icon="ArrowRight" circle @click="$emit('next')" />
          <div class="lightbox-actions">
            <el-button
              text
              :type="currentPhoto?.is_favorite ? 'warning' : 'default'"
              :icon="currentPhoto?.is_favorite ? StarFilled : Star"
              @click.stop="toggleFavorite"
            />
            <el-button text :icon="Close" circle @click="$emit('close')" />
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
import { ArrowLeft, ArrowRight, Close, Star, StarFilled } from '@element-plus/icons-vue'
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
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  color: #fff;
  z-index: 10;
  gap: 8px;
}
.lightbox-counter {
  font-size: 14px;
  color: #ccc;
  user-select: none;
}
.lightbox-actions {
  margin-left: auto;
  display: flex;
  gap: 4px;
}
.lightbox-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 60px 40px 40px;
  box-sizing: border-box;
}
.lightbox-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
  user-select: none;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
