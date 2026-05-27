<template>
  <div class="folder-page">
    <div class="folder-toolbar">
      <SegmentedControl
        v-model="viewMode"
        :options="[
          { label: '文件夹视图', value: 'folders' },
          { label: '聚合视图', value: 'aggregate' },
        ]"
      />
    </div>

    <div v-if="viewMode === 'folders'" class="folders-grid">
      <div v-if="!folderData" class="loading-wrap">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else-if="folderData.items.length === 0" class="empty-wrap">
        <div class="empty-icon-float">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
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
          @mouseenter="onCardMouseEnter($event)"
          @mouseleave="onCardMouseLeave($event)"
          @mousemove="onCardMouseMove($event)"
        >
          <div class="folder-cover">
            <img
              v-if="folder.cover_photo?.thumbnail_path"
              :src="`/thumbnails/${folder.cover_photo.thumbnail_path}`"
              loading="lazy"
            />
            <div v-else class="folder-cover-empty">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <div class="folder-cover-glow" />
          </div>
          <div class="folder-info">
            <span class="folder-name">{{ folder.name }}</span>
            <span class="folder-count">{{ folder.photo_count }} 张照片</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="aggregate-content">
      <div v-if="currentFolder" class="current-folder-bar">
        <button class="pill-btn" @click="currentFolder = ''; fetchAllPhotos()">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12" /><polyline points="12 19 5 12 12 5" />
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

// 3D tilt hover effect
function onCardMouseEnter(e: MouseEvent) {
  const card = e.currentTarget as HTMLElement
  card.style.transition = 'transform 0.15s ease, box-shadow 0.3s var(--ease-apple)'
}

function onCardMouseLeave(e: MouseEvent) {
  const card = e.currentTarget as HTMLElement
  card.style.transition = 'all 400ms var(--ease-apple)'
  card.style.transform = ''
}

function onCardMouseMove(e: MouseEvent) {
  const card = e.currentTarget as HTMLElement
  const rect = card.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  const rotateX = ((y - centerY) / centerY) * -3
  const rotateY = ((x - centerX) / centerX) * 3

  card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`
}
</script>

<style scoped>
.folder-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.folder-toolbar {
  display: flex;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  gap: var(--space-md);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-color);
}

[data-theme="dark"] .folder-toolbar {
  background: rgba(255, 255, 255, 0.03);
}

.folders-grid {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-xl);
}

.folder-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-lg);
}

/* ===== 文件夹卡片 — 3D 倾斜 ===== */
.folder-card {
  border-radius: var(--radius-xl);
  overflow: hidden;
  cursor: pointer;
  transition: all 220ms cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: var(--card-shadow);
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  border: 1px solid var(--border-glass);
  animation: stagger-in 0.5s var(--ease-apple) both;
  will-change: transform;
}

.folder-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.folder-cover {
  height: 160px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.folder-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-apple);
}

.folder-card:hover .folder-cover img {
  transform: scale(1.06);
}

.folder-cover-empty {
  color: var(--text-tertiary);
  opacity: 0.3;
}

.folder-cover-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, transparent 50%);
}

.folder-card:hover .folder-cover-glow {
  opacity: 1;
}

.folder-info {
  padding: var(--space-md) var(--space-lg);
}

.folder-name {
  display: block;
  font-size: var(--text-base);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-count {
  font-size: var(--text-sm);
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
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-color);
}

.current-folder-name {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.loading-wrap, .empty-wrap {
  padding: var(--space-xl);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  color: var(--text-tertiary);
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
