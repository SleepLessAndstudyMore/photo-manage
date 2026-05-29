<template>
  <div class="folder-page">
    <div class="page-header">
      <h2 class="page-title">文件夹</h2>
      <div class="header-actions">
        <SegmentedControl
        v-model="viewMode"
        :options="[
          { label: '文件夹视图', value: 'folders' },
          { label: '聚合视图', value: 'aggregate' },
        ]"
      />
      </div>
    </div>

    <div v-if="viewMode === 'folders'" class="folders-grid">
      <div v-if="!folderData" class="loading-wrap">
        <el-skeleton :rows="3" animated />
      </div>
      <EmptyState
        v-else-if="folderData.items.length === 0"
        type="folder"
        title="暂无文件夹"
        subtitle="添加图库源后，文件夹将在这里显示"
      />
      <div v-else class="folder-cards">
        <div
          v-for="(folder, index) in folderData.items"
          :key="folder.path"
          class="folder-card"
          :style="{ animationDelay: `${Math.min(index * 40, 400)}ms` }"
          @click="enterFolder(folder.path)"
        >
          <!-- 拼贴封面 -->
          <div class="folder-cover"
               :class="{ 'has-photos': folder.preview_photos && folder.preview_photos.length > 0 }"
          >
            <!-- 有照片时显示2x2拼贴 -->
            <template v-if="folder.preview_photos && folder.preview_photos.length > 0">
              <div class="collage-grid">
                <div
                  v-for="(p, i) in folder.preview_photos.slice(0, 4)"
                  :key="i"
                  class="collage-item"
                >
                  <img
                    v-if="p.thumbnail_path"
                    :src="`/thumbnails/${p.thumbnail_path}`"
                    loading="lazy"
                  />
                </div>
              </div>
            </template>
            <!-- 无照片时显示品牌渐变占位 -->
            <div v-else class="folder-cover-empty">
              <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="white" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <!-- 底部渐变遮罩 + 文字 -->
            <div class="folder-cover-overlay">
              <span class="folder-name-overlay">{{ folder.name }}</span>
              <span class="folder-count-overlay">{{ folder.photo_count }} 张</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="aggregate-content">
      <div v-if="currentFolder" class="current-folder-bar">
        <button class="pill-btn" @click="currentFolder = ''; fetchAllPhotos()">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
          </svg>
          返回全部
        </button>
        <span class="current-folder-name">{{ currentFolder }}</span>
      </div>
      <PhotoGrid
        :photos="photos"
        :loading="loading"
        empty-text="暂无照片"
        @photo-click="onPhotoClick"
        @load-more="onLoadMore"
        @toggle-favorite="onToggleFavorite"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePhotoStore } from '@/stores/photo'
import type { Photo } from '@/types/photo'
import PhotoGrid from '@/components/PhotoGrid.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()
const photoStore = usePhotoStore()

const viewMode = ref<'folders' | 'aggregate'>('folders')
const currentFolder = ref('')

const folderData = computed(() => photoStore.folders)
const photos = computed(() => photoStore.photos)
const loading = computed(() => photoStore.loading)

onMounted(async () => {
  await photoStore.fetchFolders()
})

watch(viewMode, async (mode) => {
  if (mode === 'aggregate') {
    await fetchAllPhotos()
  }
})

async function fetchAllPhotos() {
  await photoStore.fetchPhotos({ page: 1, page_size: 50 })
}

async function enterFolder(folderPath: string) {
  currentFolder.value = folderPath
  viewMode.value = 'aggregate'
  await photoStore.fetchPhotos({ folder: folderPath, page: 1, page_size: 50 })
}

function onPhotoClick(photo: Photo) {
  router.push(`/photos/${photo.id}`)
}

async function onLoadMore() {
  await photoStore.loadMore()
}

async function onToggleFavorite(photoId: number, isFavorite: boolean) {
  await photoStore.updateMetadata(photoId, { is_favorite: isFavorite })
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.folder-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--space-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: var(--text-h1);
  font-weight: var(--font-weight-bold);
  letter-spacing: var(--tracking-tight);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.folder-toolbar {
  display: flex;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  gap: var(--space-4);
  flex-shrink: 0;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.folders-grid {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.folder-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-4);
}

/* ===== 文件夹卡片 ===== */
.folder-card {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 200ms var(--ease-standard), box-shadow 200ms var(--ease-standard);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  animation: stagger-in 0.35s var(--ease-standard) backwards;
  position: relative;
}

.folder-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
  border-color: var(--accent);
}

/* ===== 拼贴封面 ===== */
.folder-cover {
  height: 160px;
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.folder-cover.has-photos {
  background: var(--gray-100);
}

.collage-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  width: 100%;
  height: 100%;
  gap: 2px;
}

.collage-item {
  overflow: hidden;
  background: var(--gray-200);
}

.collage-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 300ms var(--ease-standard);
}

.folder-card:hover .collage-item img {
  transform: scale(1.05);
}

/* 无照片时的占位 */
.folder-cover-empty {
  color: white;
  opacity: 0.6;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 底部渐变遮罩 + 文字 */
.folder-cover-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px 12px 10px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.folder-name-overlay {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.folder-count-overlay {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.aggregate-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.current-folder-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-6);
  background: var(--bg-card);
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-color);
}

.current-folder-name {
  font-size: var(--text-caption);
  color: var(--text-secondary);
}

.loading-wrap, .empty-wrap {
  padding: var(--space-6);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  color: var(--text-placeholder);
}

.empty-icon-float {
  opacity: 0.3;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
</style>
