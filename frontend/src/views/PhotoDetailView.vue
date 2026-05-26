<template>
  <div class="photo-detail-page">
    <div class="detail-toolbar">
      <el-button text :icon="ArrowLeft" @click="goBack">返回</el-button>
      <span class="detail-filename">{{ photo?.file_name || '加载中...' }}</span>
      <div class="detail-actions">
        <el-button
          text
          :type="photo?.is_favorite ? 'warning' : 'default'"
          :icon="photo?.is_favorite ? StarFilled : Star"
          @click="toggleFavorite"
        >
          {{ photo?.is_favorite ? '已收藏' : '收藏' }}
        </el-button>
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
      <div class="detail-preview" @click="showLightbox = true">
        <img
          v-if="photo?.preview_path"
          :src="`/thumbnails/${photo.preview_path}`"
          :alt="photo.file_name"
          class="preview-img"
        />
        <img
          v-else-if="photo?.thumbnail_path"
          :src="`/thumbnails/${photo.thumbnail_path}`"
          :alt="photo.file_name"
          class="preview-img"
        />
        <div v-else class="preview-placeholder">
          <el-icon :size="48"><PictureFilled /></el-icon>
          <p>暂无预览</p>
        </div>
        <div v-if="photo?.file_missing" class="missing-banner">
          文件丢失 — 原始文件已被移动或删除
        </div>
      </div>
      <aside class="detail-sidebar">
        <ExifPanel
          :exif="photoExif"
          :loading="exifLoading"
        />
      </aside>
    </div>

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
import { ArrowLeft, Star, StarFilled, PictureFilled } from '@element-plus/icons-vue'
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
  height: calc(100vh - 52px);
}
.detail-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid var(--color-border, #e8e8e8);
  gap: 12px;
  flex-shrink: 0;
}
.detail-filename {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.detail-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.detail-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.detail-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-secondary, #1a1a1a);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.preview-placeholder {
  text-align: center;
  color: var(--color-text-secondary, #999);
}
.missing-banner {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 77, 79, 0.9);
  color: #fff;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 14px;
}
.detail-sidebar {
  width: 300px;
  min-width: 300px;
  border-left: 1px solid var(--color-border, #e8e8e8);
  overflow-y: auto;
  padding: 16px;
  background: var(--color-bg-primary, #fff);
}
</style>
