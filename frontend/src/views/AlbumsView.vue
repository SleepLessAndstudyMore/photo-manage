<template>
  <div class="view-albums">
    <div class="albums-header">
      <h2 class="albums-title">相册</h2>
      <button class="pill-btn pill-btn--primary" @click="showCreateDialog = true">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        新建相册
      </button>
    </div>

    <div v-if="loading" class="albums-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="albums.length === 0" class="albums-empty">
      <div class="empty-icon-float">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" />
        </svg>
      </div>
      <p>暂无相册</p>
      <p class="text-secondary">点击上方按钮创建你的第一个相册</p>
    </div>

    <div v-else class="albums-grid">
      <div
        v-for="(album, index) in albums"
        :key="album.id"
        class="album-card"
        :style="{ animationDelay: `${Math.min(index * 40, 400)}ms` }"
        @click="goToAlbum(album.id)"
      >
        <div class="album-cover">
          <img
            v-if="album.cover_thumbnail"
            :src="`/thumbnails/${album.cover_thumbnail}`"
            :alt="album.name"
            loading="lazy"
          />
          <div v-else class="album-cover-placeholder">
            <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" />
            </svg>
          </div>
        </div>
        <div class="album-info">
          <span class="album-name">{{ album.name }}</span>
          <span class="album-count">{{ album.photo_count }} 张</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="showCreateDialog" title="新建相册" width="400px" class="glass-dialog">
      <el-form label-position="top">
        <el-form-item label="相册名称">
          <el-input v-model="newName" placeholder="输入相册名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newDesc" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="pill-btn" @click="showCreateDialog = false">取消</button>
        <button class="pill-btn pill-btn--primary" :disabled="!newName.trim()" @click="handleCreate">创建</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
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
  overflow: hidden;
}

.albums-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  flex-shrink: 0;
}

.albums-title {
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: 200;
  letter-spacing: -1px;
}

.albums-loading { padding: 40px; }

.albums-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  gap: var(--space-md);
}

.empty-icon-float {
  opacity: 0.3;
  animation: float 4s ease-in-out infinite;
}

.text-secondary {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.albums-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-lg);
  overflow-y: auto;
}

/* ===== 相册卡片 ===== */
.album-card {
  cursor: pointer;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  border: 1px solid var(--border-glass);
  box-shadow: var(--card-shadow);
  transition: all 220ms cubic-bezier(0.22, 1, 0.36, 1);
  animation: stagger-in 0.5s var(--ease-apple) both;
}

.album-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--card-shadow-hover);
}

.album-cover {
  aspect-ratio: 16/10;
  overflow: hidden;
  background: var(--bg-secondary);
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-apple);
}

.album-card:hover .album-cover img {
  transform: scale(1.06);
}

.album-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  opacity: 0.3;
}

.album-info {
  padding: var(--space-md) var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.album-name {
  font-weight: 500;
  font-size: var(--text-base);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.album-count {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

:deep(.glass-dialog .el-dialog) {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-float);
}

[data-theme="dark"] :deep(.glass-dialog .el-dialog) {
  background: rgba(30, 30, 34, 0.8);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
</style>
