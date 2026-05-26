<template>
  <div class="view-duplicates">
    <div class="dup-header">
      <h2>重复照片清理</h2>
      <div class="dup-actions">
        <el-radio-group v-model="dupType" size="small" @change="fetchGroups">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="bitwise">完全重复</el-radio-button>
          <el-radio-button value="visual">视觉相似</el-radio-button>
        </el-radio-group>
        <el-button size="small" :loading="loading" @click="fetchGroups">刷新</el-button>
      </div>
    </div>

    <div v-if="loading" class="dup-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="groups.length === 0" class="dup-empty">
      <el-icon :size="48"><CircleCheck /></el-icon>
      <p>未发现重复或相似照片</p>
    </div>

    <div v-else class="dup-list">
      <el-card v-for="(group, idx) in groups" :key="idx" class="dup-card" shadow="hover">
        <div class="dup-card-header">
          <el-tag :type="group.type === 'bitwise' ? 'danger' : 'warning'" size="small">
            {{ group.type === 'bitwise' ? '完全重复' : '视觉相似' }}
          </el-tag>
          <span class="dup-msg">{{ group.message }}</span>
          <el-button
            v-if="group.type === 'bitwise'"
            size="small"
            type="danger"
            text
            @click="cleanGroup(group)"
          >
            删除冗余副本
          </el-button>
          <el-button
            v-else
            size="small"
            type="primary"
            text
            @click="compareGroup(group)"
          >
            对比查看
          </el-button>
        </div>
        <div class="dup-photos-row">
          <div
            v-for="photo in group.photos"
            :key="photo.id"
            class="dup-photo-item"
            :class="{ selected: selectedIds.has(photo.id) }"
            @click="toggleSelect(photo.id)"
          >
            <img
              v-if="photo.thumbnail_path"
              :src="`/thumbnails/${photo.thumbnail_path}`"
              :alt="photo.file_name"
            />
            <div v-else class="dup-photo-placeholder">
              <el-icon><PictureFilled /></el-icon>
            </div>
            <div class="dup-photo-info">
              <span class="dup-photo-name">{{ photo.file_name }}</span>
              <span class="dup-photo-size">{{ formatSize(photo.file_size) }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Compare dialog for visual similars -->
    <el-dialog v-model="compareVisible" title="对比照片" width="90%" top="3vh" destroy-on-close>
      <div class="compare-row">
        <div v-for="photo in comparePhotos" :key="photo.id" class="compare-item">
          <img
            v-if="photo.thumbnail_path"
            :src="`/thumbnails/${photo.thumbnail_path}`"
            :alt="photo.file_name"
          />
          <p class="compare-name">{{ photo.file_name }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="compareVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CircleCheck, PictureFilled } from '@element-plus/icons-vue'
import { getDuplicates } from '@/api/photos'
import { send2trash } from '@/utils/file_utils'

interface PhotoBrief {
  id: number
  file_path: string
  file_name: string
  file_size: number
  thumbnail_path: string | null
}

interface DupGroup {
  type: 'bitwise' | 'visual'
  hash?: string
  distance?: number | null
  photos: PhotoBrief[]
  suggestion: string
  message: string
}

const loading = ref(false)
const dupType = ref('all')
const groups = ref<DupGroup[]>([])
const selectedIds = ref<Set<number>>(new Set())
const compareVisible = ref(false)
const comparePhotos = ref<PhotoBrief[]>([])

onMounted(() => {
  fetchGroups()
})

async function fetchGroups() {
  loading.value = true
  try {
    const { data } = await getDuplicates({ type: dupType.value, page_size: 100 })
    groups.value = data.groups ?? []
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
}

function toggleSelect(id: number) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

async function cleanGroup(group: DupGroup) {
  const toDelete = group.photos.slice(1)
  try {
    for (const photo of toDelete) {
      await (await import('@/api/photos')).deletePhotoFile(photo.id)
    }
    fetchGroups()
  } catch {
    // ignore
  }
}

function compareGroup(group: DupGroup) {
  comparePhotos.value = group.photos
  compareVisible.value = true
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<style scoped>
.view-duplicates {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--space-lg);
}
.dup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  flex-shrink: 0;
}
.dup-header h2 { margin: 0; }
.dup-actions { display: flex; align-items: center; gap: var(--space-md); }
.dup-loading { padding: var(--space-xl); }
.dup-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #999);
  gap: var(--space-md);
}
.dup-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
.dup-card {
  --el-card-bg-color: transparent;
  --el-card-border-color: var(--border-color);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}
.dup-card:hover {
  box-shadow: var(--card-shadow-hover);
}
.dup-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}
.dup-msg { flex: 1; font-size: var(--text-sm); color: var(--text-secondary, #666); }
.dup-photos-row {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  padding-bottom: 8px;
}
.dup-photo-item {
  cursor: pointer;
  border-radius: var(--radius-sm);
  overflow: hidden;
  width: 140px;
  flex-shrink: 0;
  background: var(--bg-secondary, #f5f5f5);
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}
.dup-photo-item.selected {
  border-color: var(--accent, #7EC8C8);
}
.dup-photo-item:hover {
  box-shadow: var(--card-shadow);
}
.dup-photo-item img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}
.dup-photo-placeholder {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}
.dup-photo-info {
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.dup-photo-name {
  font-size: var(--text-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dup-photo-size {
  font-size: var(--text-sm);
  color: var(--text-secondary, #999);
}
.compare-row {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
  flex-wrap: wrap;
}
.compare-item { text-align: center; }
.compare-item img {
  max-width: 300px;
  max-height: 300px;
  border-radius: var(--radius-sm);
}
.compare-name { margin-top: 8px; font-size: var(--text-sm); }
</style>
