<template>
  <div class="view-duplicates">
    <div class="dup-header">
      <div class="dup-actions">
        <SegmentedControl
          v-model="dupType"
          :options="[
            { label: '全部', value: 'all' },
            { label: '完全重复', value: 'bitwise' },
            { label: '视觉相似', value: 'visual' },
          ]"
          @update:modelValue="fetchGroups()"
        />
        <button class="pill-btn" :disabled="loading" @click="fetchGroups">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          刷新
        </button>
      </div>
    </div>

    <div v-if="loading" class="dup-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="groups.length === 0" class="dup-empty">
      <div class="empty-icon-float">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      </div>
      <p class="empty-title">未发现重复或相似照片</p>
      <p class="text-secondary">你的照片库很干净</p>
    </div>

    <div v-else class="dup-list">
      <div v-for="(group, idx) in groups" :key="idx" class="dup-card" :style="{ animationDelay: `${Math.min(idx * 50, 400)}ms` }">
        <div class="dup-card-header">
          <span class="dup-type-badge" :class="group.type">
            {{ group.type === 'bitwise' ? '完全重复' : '视觉相似' }}
          </span>
          <span class="dup-msg">{{ group.message }}</span>
          <button
            v-if="group.type === 'bitwise'"
            class="pill-btn dup-delete-btn"
            @click="cleanGroup(group)"
          >
            删除冗余副本
          </button>
          <button
            v-else
            class="pill-btn pill-btn--primary"
            @click="compareGroup(group)"
          >
            对比查看
          </button>
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
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <div class="dup-photo-info">
              <span class="dup-photo-name">{{ photo.file_name }}</span>
              <span class="dup-photo-size">{{ formatSize(photo.file_size) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compare dialog -->
    <el-dialog v-model="compareVisible" title="对比照片" width="90%" top="3vh" destroy-on-close class="glass-dialog">
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
        <button class="pill-btn" @click="compareVisible = false">关闭</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDuplicates } from '@/api/photos'
import SegmentedControl from '@/components/SegmentedControl.vue'

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
  padding: var(--space-xl);
  overflow: hidden;
}

.dup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  flex-shrink: 0;
}

.dup-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.dup-loading { padding: var(--space-xl); }

.dup-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  gap: var(--space-md);
}

.empty-icon-float {
  color: #34C759;
  opacity: 0.4;
  animation: float 4s ease-in-out infinite;
}

.empty-title {
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--text-secondary);
}

.text-secondary {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.dup-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ===== 重复卡片 ===== */
.dup-card {
  flex-shrink: 0;
  background: var(--card-bg);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--card-shadow);
  transition: all var(--transition-fast);
  animation: stagger-in 0.5s var(--ease-apple) both;
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

.dup-type-badge {
  padding: 4px 12px;
  border-radius: 100px;
  font-size: var(--text-xs);
  font-weight: 600;
}

.dup-type-badge.bitwise {
  background: rgba(255, 59, 48, 0.12);
  color: #FF3B30;
}

.dup-type-badge.visual {
  background: rgba(255, 149, 0, 0.12);
  color: #FF9500;
}

.dup-msg {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.dup-delete-btn {
  color: #FF3B30;
}

.dup-delete-btn:hover {
  background: rgba(255, 59, 48, 0.1);
}

.dup-photos-row {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  padding-bottom: var(--space-xs);
}

.dup-photo-item {
  cursor: pointer;
  border-radius: var(--radius-md);
  overflow: hidden;
  width: 150px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  transition: all 220ms var(--ease-apple);
}

.dup-photo-item.selected {
  border-color: var(--accent);
  box-shadow: 0 0 16px var(--accent-glow);
}

.dup-photo-item:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.dup-photo-item img {
  width: 100%;
  height: 130px;
  object-fit: cover;
  display: block;
}

.dup-photo-placeholder {
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.dup-photo-info {
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dup-photo-name {
  font-size: var(--text-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dup-photo-size {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.compare-row {
  display: flex;
  gap: var(--space-lg);
  justify-content: center;
  flex-wrap: wrap;
}

.compare-item { text-align: center; }

.compare-item img {
  max-width: 320px;
  max-height: 320px;
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
}

.compare-name {
  margin-top: var(--space-sm);
  font-size: var(--text-sm);
  color: var(--text-secondary);
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
