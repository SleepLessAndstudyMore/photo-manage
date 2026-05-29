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

    <EmptyState
      v-else-if="groups.length === 0"
      type="clean"
      title="未发现重复或相似照片"
      subtitle="你的照片库很干净"
    />

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
import EmptyState from '@/components/EmptyState.vue'

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
  padding: var(--space-6);
  overflow: hidden;
}

.dup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  flex-shrink: 0;
}

.dup-actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.dup-loading { padding: var(--space-6); }

.dup-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  gap: var(--space-4);
}

.empty-icon-float {
  color: var(--success-500);
  opacity: 0.4;
  animation: float 4s ease-in-out infinite;
}

.empty-title {
  font-size: var(--text-h3);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.text-secondary {
  color: var(--text-secondary);
  font-size: var(--text-body);
}

.dup-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ===== 重复卡片 ===== */
.dup-card {
  flex-shrink: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: var(--shadow-xs);
  transition: box-shadow var(--transition-fast);
  animation: stagger-in 0.4s var(--transition-normal) backwards;
}

.dup-card:hover {
  box-shadow: var(--shadow-sm);
}

.dup-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.dup-type-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-caption);
  font-weight: var(--font-weight-semibold);
}

.dup-type-badge.bitwise {
  background: var(--danger-100);
  color: var(--danger-500);
}

.dup-type-badge.visual {
  background: var(--warning-100);
  color: var(--warning-500);
}

.dup-msg {
  flex: 1;
  font-size: var(--text-body);
  color: var(--text-secondary);
}

.dup-delete-btn {
  color: var(--danger-500);
}

.dup-delete-btn:hover {
  background: var(--danger-100);
}

.dup-photos-row {
  display: flex;
  gap: var(--space-3);
  overflow-x: auto;
  padding-bottom: var(--space-1);
}

.dup-photo-item {
  cursor: pointer;
  border-radius: var(--radius-sm);
  overflow: hidden;
  width: 150px;
  flex-shrink: 0;
  background: var(--gray-100);
  border: 2px solid transparent;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.dup-photo-item.selected {
  border-color: var(--accent);
  box-shadow: 0 0 12px var(--accent-glow);
}

.dup-photo-item:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px) scale(1.03);
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
  color: var(--text-placeholder);
}

.dup-photo-info {
  padding: var(--space-2) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dup-photo-name {
  font-size: var(--text-caption);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dup-photo-size {
  font-size: var(--text-caption);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.compare-row {
  display: flex;
  gap: var(--space-6);
  justify-content: center;
  flex-wrap: wrap;
}

.compare-item { text-align: center; }

.compare-item img {
  max-width: 320px;
  max-height: 320px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.compare-name {
  margin-top: var(--space-2);
  font-size: var(--text-body);
  color: var(--text-secondary);
}

:deep(.glass-dialog .el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
</style>
