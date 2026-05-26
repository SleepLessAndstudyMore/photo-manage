<template>
  <div class="folder-page">
    <div class="folder-toolbar">
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button value="folders">文件夹视图</el-radio-button>
        <el-radio-button value="aggregate">聚合视图</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="viewMode === 'folders'" class="folders-grid">
      <div v-if="!folderData" class="loading-wrap">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else-if="folderData.items.length === 0" class="empty-wrap">
        <el-empty description="暂无文件夹" />
      </div>
      <div v-else class="folder-cards">
        <div
          v-for="folder in folderData.items"
          :key="folder.path"
          class="folder-card"
          @click="enterFolder(folder.path)"
        >
          <div class="folder-cover">
            <img
              v-if="folder.cover_photo?.thumbnail_path"
              :src="`/thumbnails/${folder.cover_photo.thumbnail_path}`"
              loading="lazy"
            />
            <el-icon v-else :size="32"><FolderOpened /></el-icon>
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
        <el-button text @click="currentFolder = ''; fetchAllPhotos()">
          <el-icon><ArrowLeft /></el-icon> 返回全部
        </el-button>
        <span>{{ currentFolder }}</span>
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
import { FolderOpened, ArrowLeft } from '@element-plus/icons-vue'
import { usePhotoStore } from '@/stores/photo'
import type { Photo } from '@/types/photo'
import PhotoGrid from '@/components/PhotoGrid.vue'

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
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
}
.folders-grid {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
}
.folder-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-md);
}
.folder-card {
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--card-shadow);
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
}
.folder-card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}
.folder-cover {
  height: 140px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.folder-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.folder-info {
  padding: var(--space-sm) var(--space-md);
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
  color: var(--text-secondary);
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
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  font-size: var(--text-sm);
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-color);
}
.loading-wrap, .empty-wrap {
  padding: var(--space-xl);
  text-align: center;
}
</style>
