<template>
  <div class="view-albums">
    <div class="albums-header">
      <h2>相册</h2>
      <el-button size="small" type="primary" @click="showCreateDialog = true">新建相册</el-button>
    </div>

    <div v-if="loading" class="albums-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="albums.length === 0" class="albums-empty">
      <el-icon :size="48"><FolderOpened /></el-icon>
      <p>暂无相册，点击上方按钮创建</p>
    </div>

    <div v-else class="albums-grid">
      <div
        v-for="album in albums"
        :key="album.id"
        class="album-card"
        @click="goToAlbum(album.id)"
      >
        <div class="album-cover">
          <img
            v-if="album.cover_thumbnail"
            :src="`/thumbnails/${album.cover_thumbnail}`"
            :alt="album.name"
          />
          <div v-else class="album-cover-placeholder">
            <el-icon :size="36"><FolderOpened /></el-icon>
          </div>
        </div>
        <div class="album-info">
          <span class="album-name">{{ album.name }}</span>
          <span class="album-count">{{ album.photo_count }} 张</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="showCreateDialog" title="新建相册" width="400px">
      <el-form label-position="top">
        <el-form-item label="相册名称">
          <el-input v-model="newName" placeholder="输入相册名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newDesc" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :disabled="!newName.trim()" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOpened } from '@element-plus/icons-vue'
import { getAlbums, createAlbum } from '@/api/albums'

interface AlbumItem {
  id: number
  name: string
  description: string | null
  cover_photo_id: number | null
  photo_count: number
  cover_thumbnail: string | null
}

const router = useRouter()
const albums = ref<AlbumItem[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const newName = ref('')
const newDesc = ref('')

onMounted(() => {
  fetchAlbums()
})

async function fetchAlbums() {
  loading.value = true
  try {
    const { data } = await getAlbums({ page_size: 200 })
    albums.value = data.items ?? []
  } finally {
    loading.value = false
  }
}

function goToAlbum(id: number) {
  router.push(`/albums/${id}`)
}

async function handleCreate() {
  if (!newName.value.trim()) return
  await createAlbum({ name: newName.value.trim(), description: newDesc.value.trim() || undefined })
  newName.value = ''
  newDesc.value = ''
  showCreateDialog.value = false
  fetchAlbums()
}
</script>

<style scoped>
.view-albums {
  height: 100%;
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
}
.albums-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  flex-shrink: 0;
}
.albums-header h2 {
  margin: 0;
  font-size: var(--text-2xl);
}
.albums-loading { padding: 40px; }
.albums-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  gap: var(--space-md);
}
.albums-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-md);
  overflow-y: auto;
}
.album-card {
  cursor: pointer;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  border: 1px solid var(--border-color);
  box-shadow: var(--card-shadow);
  transition: all var(--transition-fast);
}
.album-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}
.album-cover {
  aspect-ratio: 16/9;
  overflow: hidden;
  background: var(--bg-secondary);
}
.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.album-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}
.album-info {
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.album-name {
  font-weight: 600;
  font-size: var(--text-base);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.album-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
</style>
