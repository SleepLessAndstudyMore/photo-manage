<template>
  <div class="photo-detail-page">
    <!-- 顶部工具栏 -->
    <div class="detail-toolbar">
      <button class="pill-btn" @click="goBack">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
        </svg>
        返回
      </button>
      <span class="detail-filename">{{ photo?.file_name || '加载中...' }}</span>
      <div class="detail-actions">
        <button
          class="pill-btn"
          :class="{ 'pill-btn--primary': photo?.is_favorite }"
          @click="toggleFavorite"
        >
          <svg v-if="photo?.is_favorite" viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          {{ photo?.is_favorite ? '已收藏' : '收藏' }}
        </button>
        <el-rate
          v-if="photo"
          v-model="rating"
          :max="5"
          size="small"
          @change="updateRating"
        />
      </div>
    </div>

    <div class="detail-body">
      <!-- 左侧：照片大图预览（60%） -->
      <div class="detail-preview" @click="showLightbox = true">
        <img
          v-if="photo?.preview_path"
          :src="`/thumbnails/${photo.preview_path}`"
          :alt="photo.file_name"
          class="detail-image"
        />
        <img
          v-else-if="photo?.thumbnail_path"
          :src="`/thumbnails/${photo.thumbnail_path}`"
          :alt="photo.file_name"
          class="detail-image"
        />
        <div v-else class="preview-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
          </svg>
          <p>暂无预览</p>
        </div>
        <div v-if="photo?.file_missing" class="missing-banner">
          文件丢失 — 原始文件已被移动或删除
        </div>
      </div>

      <!-- 右侧：信息面板（40%） -->
      <aside class="drawer-panel">
        <ExifPanel
          :exif="photoExif"
          :loading="exifLoading"
        />
      </aside>
    </div>

    <!-- Lightbox -->
    <PhotoDetail
      :photos="allPhotos"
      :current-index="currentIndex"
      :visible="showLightbox"
      @close="showLightbox = false"
      @prev="navigate(-1)"
      @next="navigate(1)"
      @update:favorite="onFavoriteUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePhotoStore } from '@/stores/photo'
import type { PhotoDetail as PhotoDetailType } from '@/types/photo'
import ExifPanel from '@/components/ExifPanel.vue'
import PhotoDetail from '@/components/PhotoDetail.vue'

const route = useRoute()
const router = useRouter()
const photoStore = usePhotoStore()

const photoId = computed(() => Number(route.params.id))
const showLightbox = ref(false)
const rating = ref(0)

const photo = computed(() => photoStore.currentPhoto)
const photoExif = computed(() => photoStore.currentExif)
const exifLoading = ref(false)
const allPhotos = computed(() => photoStore.photos)
const currentIndex = computed(() =>
  allPhotos.value.findIndex(p => p.id === photoId.value)
)

onMounted(async () => {
  try {
    await photoStore.fetchPhotoById(photoId.value)
    exifLoading.value = true
    await photoStore.fetchExif(photoId.value)
  } finally {
    exifLoading.value = false
  }
  if (photo.value) {
    rating.value = photo.value.rating
  }
})

function goBack() {
  router.back()
}

async function toggleFavorite() {
  if (!photo.value) return
  await photoStore.updateMetadata(photo.value.id, {
    is_favorite: !photo.value.is_favorite,
  })
}

async function updateRating(val: number) {
  if (!photo.value) return
  await photoStore.updateMetadata(photo.value.id, { rating: val })
}

function navigate(delta: number) {
  const newIdx = currentIndex.value + delta
  if (newIdx >= 0 && newIdx < allPhotos.value.length) {
    const p = allPhotos.value[newIdx]
    router.replace(`/photos/${p.id}`)
  }
}

async function onFavoriteUpdate(photoId: number, isFavorite: boolean) {
  await photoStore.updateMetadata(photoId, { is_favorite: isFavorite })
}
</script>

<style scoped>
.photo-detail-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background: var(--bg-primary);
}

/* ===== 顶部工具栏 ===== */
.detail-toolbar {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-6);
  gap: var(--space-4);
  flex-shrink: 0;
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  border-bottom: 1px solid var(--border-color);
  height: 56px;
}

.detail-filename {
  flex: 1;
  font-size: var(--text-body);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
  color: var(--text-primary);
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* ===== 主体 ===== */
.detail-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧照片预览（60%） */
.detail-preview {
  flex: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  padding: var(--space-6);
  background: #ffffff;
}

.detail-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: var(--radius-sm);
  box-shadow: 0 16px 64px rgba(0, 0, 0, 0.4);
  transition: transform var(--transition-normal);
}

.detail-image:hover {
  transform: scale(1.01);
}

.preview-placeholder {
  text-align: center;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.missing-banner {
  position: absolute;
  top: var(--space-4);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 77, 79, 0.9);
  color: #fff;
  padding: 8px 20px;
  border-radius: 100px;
  font-size: var(--text-caption);
  backdrop-filter: blur(8px);
}

/* 右侧信息面板（40%） */
.drawer-panel {
  width: 380px;
  min-width: 380px;
  height: 100%;
  overflow-y: auto;
  padding: var(--space-4) var(--space-6);
  background: var(--bg-card);
  border-left: 1px solid var(--border-color);
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .drawer-panel {
    width: 320px;
    min-width: 320px;
  }
}

@media (max-width: 768px) {
  .detail-body {
    flex-direction: column;
  }
  .detail-preview {
    flex: none;
    height: 50%;
  }
  .drawer-panel {
    width: 100%;
    min-width: 100%;
    border-left: none;
    border-top: 1px solid var(--border-color);
  }
}

[data-theme="dark"] .detail-preview {
  background: #0F172A;
}
</style>
