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
  height: calc(100vh - 52px);
}
.folder-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  gap: 16px;
  border-bottom: 1px solid var(--color-border, #e8e8e8);
  flex-shrink: 0;
}
.folders-grid {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.folder-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
.folder-card {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--color-border, #e8e8e8);
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.folder-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.folder-cover {
  height: 140px;
  background: var(--color-bg-secondary, #f0f0f0);
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
  padding: 10px 12px;
}
.folder-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.folder-count {
  font-size: 12px;
  color: var(--color-text-secondary, #999);
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
  gap: 8px;
  padding: 8px 20px;
  background: var(--color-bg-secondary, #fafafa);
  font-size: 13px;
  flex-shrink: 0;
}
.loading-wrap, .empty-wrap {
  padding: 40px;
  text-align: center;
}
</style>
