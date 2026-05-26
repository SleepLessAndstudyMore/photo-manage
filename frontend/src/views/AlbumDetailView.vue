<template>
  <div class="album-detail-page">
    <div class="album-toolbar">
      <el-button text :icon="ArrowLeft" @click="goBack">返回</el-button>
      <span class="album-title">{{ album?.name || '加载中...' }}</span>
      <div class="album-actions">
        <el-button size="small" text @click="showEditDialog = true">编辑相册</el-button>
      </div>
    </div>

    <div v-if="album?.description" class="album-desc">
      {{ album.description }}
    </div>

    <div v-if="loading" class="album-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="photos.length === 0" class="album-empty">
      <el-icon :size="48"><FolderOpened /></el-icon>
      <p>相册中暂无照片</p>
      <p class="text-secondary">在照片详情页可以将照片添加到该相册</p>
    </div>

    <div v-else class="album-photos-grid">
      <div
        v-for="photo in photos"
        :key="photo.id"
        class="album-photo-item"
        @click="goToPhoto(photo.id)"
      >
        <img
          v-if="photo.thumbnail_path"
          :src="`/thumbnails/${photo.thumbnail_path}`"
          :alt="photo.file_name"
        />
        <div v-else class="photo-placeholder">
          <el-icon><PictureFilled /></el-icon>
        </div>
        <div class="photo-overlay">
          <el-button
            size="small"
            text
            type="danger"
            @click.stop="removePhoto(photo.id)"
          >
            移除
          </el-button>
        </div>
      </div>
    </div>

    <!-- Edit album dialog -->
    <el-dialog v-model="showEditDialog" title="编辑相册" width="400px">
      <el-form label-position="top">
        <el-form-item label="相册名称">
          <el-input v-model="editName" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editDesc" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateAlbum">保存</el-button>
        <el-button type="danger" text @click="handleDeleteAlbum">删除相册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, FolderOpened, PictureFilled } from '@element-plus/icons-vue'
import { getAlbum, getAlbumPhotos, updateAlbum, deleteAlbum, removePhotoFromAlbum } from '@/api/albums'

interface AlbumItem {
  id: number
  name: string
  description: string | null
  cover_photo_id: number | null
  photo_count: number
  cover_thumbnail: string | null
}

interface PhotoItem {
  id: number
  file_name: string
  thumbnail_path: string | null
}

const route = useRoute()
const router = useRouter()
const albumId = computed(() => Number(route.params.id))

const album = ref<AlbumItem | null>(null)
const photos = ref<PhotoItem[]>([])
const loading = ref(false)
const showEditDialog = ref(false)
const editName = ref('')
const editDesc = ref('')

onMounted(async () => {
  await loadAlbum()
  await loadPhotos()
})

async function loadAlbum() {
  try {
    const { data } = await getAlbum(albumId.value)
    album.value = data
    editName.value = data.name
    editDesc.value = data.description ?? ''
  } catch {
    // not found
  }
}

async function loadPhotos() {
  loading.value = true
  try {
    const { data } = await getAlbumPhotos(albumId.value, { page_size: 200 })
    photos.value = data.items ?? []
  } catch {
    photos.value = []
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function goToPhoto(id: number) {
  router.push(`/photos/${id}`)
}

async function removePhoto(photoId: number) {
  try {
    await removePhotoFromAlbum(albumId.value, photoId)
    photos.value = photos.value.filter(p => p.id !== photoId)
    if (album.value) {
      album.value.photo_count = photos.value.length
    }
  } catch {
    // ignore
  }
}

async function handleUpdateAlbum() {
  try {
    await updateAlbum(albumId.value, { name: editName.value, description: editDesc.value })
    if (album.value) {
      album.value.name = editName.value
      album.value.description = editDesc.value
    }
    showEditDialog.value = false
  } catch {
    // ignore
  }
}

async function handleDeleteAlbum() {
  try {
    await deleteAlbum(albumId.value)
    router.back()
  } catch {
    // ignore
  }
}
</script>

<style scoped>
.album-detail-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0 var(--space-xl);
}
.album-toolbar {
  display: flex;
  align-items: center;
  padding: var(--space-md) 0;
  gap: var(--space-md);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}
.album-title {
  flex: 1;
  font-size: var(--text-lg);
  font-weight: 600;
}
.album-desc {
  padding: var(--space-md) 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  flex-shrink: 0;
}
.album-loading { padding: 40px; }
.album-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  gap: var(--space-md);
}
.album-photos-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-md);
  overflow-y: auto;
  padding: var(--space-md) 0;
}
.album-photo-item {
  cursor: pointer;
  border-radius: var(--radius-sm);
  overflow: hidden;
  position: relative;
  aspect-ratio: 1;
  background: var(--bg-secondary);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}
.album-photo-item:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}
.album-photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}
.photo-overlay {
  position: absolute;
  top: 6px;
  right: 6px;
  opacity: 0;
  transition: all var(--transition-fast);
}
.album-photo-item:hover .photo-overlay {
  opacity: 1;
}
</style>
