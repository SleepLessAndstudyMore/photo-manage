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
      <div v-else-if="folderData.items.length === 0" class="empty-wrap">
        <div class="empty-icon-float">
          <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <p>暂无文件夹</p>
      </div>
      <div v-else class="folder-cards">
        <div
          v-for="(folder, index) in folderData.items"
          :key="folder.path"
          class="folder-card"
          :style="{ animationDelay: `${Math.min(index * 40, 400)}ms` }"
          @click="enterFolder(folder.path)"
        >
          <div class="folder-cover">
            <img
              v-if="folder.cover_photo?.thumbnail_path"
              :src="`/thumbnails/${folder.cover_photo.thumbnail_path}`"
              loading="lazy"
            />
            <div v-else class="folder-cover-empty">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
          </div>
          <div class="folder-info">
            <span class="folder-name">{{ folder.name }}</span>
            <span class="folder-meta">{{ folder.photo_count }} 张照片 · {{ formatDate(folder.modified_at) }}</span>
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
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  animation: stagger-in 0.4s var(--transition-normal) backwards;
}

.folder-card:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15), 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-6px) scale(1.02);
  border-color: var(--accent);
}

.folder-cover {
  height: 140px;
  background: var(--gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.folder-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.folder-card:hover .folder-cover img {
  transform: scale(1.05);
}

.folder-cover-empty {
  color: var(--text-placeholder);
  opacity: 0.3;
}

.folder-info {
  padding: var(--space-3) var(--space-4);
}

.folder-name {
  display: block;
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-meta {
  font-size: var(--text-caption);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
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
