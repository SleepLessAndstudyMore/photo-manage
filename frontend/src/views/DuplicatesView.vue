<template>
  <div class="view-duplicates">
    <div class="page-header">
      <h2 class="page-title">清理</h2>
      <div class="header-actions">
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

    <!-- 顶部统计 -->
    <div v-if="groups.length > 0 && !loading" class="stats-bar">
      <div class="stat-item">
        <span class="stat-value stat-value--highlight">{{ totalDuplicates }}</span>
        <span class="stat-label">重复照片</span>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <span class="stat-value">{{ totalGroups }}</span>
        <span class="stat-label">重复组</span>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <span class="stat-value stat-value--danger">{{ formatSize(totalWasteSize) }}</span>
        <span class="stat-label">可释放空间</span>
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
      <div
        v-for="(group, idx) in groups"
        :key="idx"
        class="dup-card"
        :style="{ animationDelay: `${Math.min(idx * 50, 400)}ms` }"
      >
        <div class="dup-card-header">
          <div class="dup-card-header-left">
            <span class="dup-type-badge" :class="group.type">
              {{ group.type === 'bitwise' ? '完全重复' : '视觉相似' }}
            </span>
            <span class="dup-count">{{ group.photos.length }} 张照片</span>
          </div>
          <div class="dup-card-header-right">
            <button
              v-if="group.type === 'bitwise'"
              class="dup-action-btn dup-action-btn--danger"
              @click="confirmClean(group)"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              删除冗余
            </button>
            <button
              v-else
              class="dup-action-btn"
              @click="compareGroup(group)"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              对比查看
            </button>
          </div>
        </div>

        <div class="dup-photos-row">
          <div
            v-for="(photo, pIdx) in group.photos"
            :key="photo.id"
            class="dup-photo-item"
            :class="{ 'is-original': pIdx === 0, 'is-duplicate': pIdx > 0 }"
            @click="toggleSelect(photo.id)"
          >
            <div class="dup-photo-thumb">
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
              <div v-if="pIdx === 0" class="photo-badge photo-badge--original">原图</div>
              <div v-else class="photo-badge photo-badge--dup">副本</div>
            </div>
            <div class="dup-photo-info">
              <span class="dup-photo-name">{{ photo.file_name }}</span>
              <span class="dup-photo-size">{{ formatSize(photo.file_size) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 清理确认模态框 -->
    <el-dialog
      v-model="confirmVisible"
      title="确认删除"
      width="480px"
      class="glass-dialog"
      destroy-on-close
    >
      <div class="confirm-content">
        <div class="confirm-icon">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <h4 class="confirm-title">确定删除 {{ confirmCount }} 张重复照片？</h4>
        <p class="confirm-subtitle">此操作不可撤销，将释放 {{ confirmSize }} 空间</p>
        <div class="confirm-preview">
          <div
            v-for="photo in confirmPhotos.slice(0, 6)"
            :key="photo.id"
            class="confirm-thumb"
          >
            <img v-if="photo.thumbnail_path" :src="`/thumbnails/${photo.thumbnail_path}`" />
          </div>
        </div>
      </div>
      <template #footer>
        <button class="pill-btn" @click="confirmVisible = false">取消</button>
        <button class="pill-btn pill-btn--danger" :disabled="cleaning" @click="doClean">
          <span v-if="cleaning" class="spinner-sm" />
          <span v-else>确认删除</span>
        </button>
      </template>
    </el-dialog>

    <!-- 对比对话框 -->
    <el-dialog v-model="compareVisible" title="对比照片" width="90%" top="3vh" destroy-on-close class="glass-dialog">
      <div class="compare-row">
        <div v-for="photo in comparePhotos" :key="photo.id" class="compare-item">
          <img
            v-if="photo.thumbnail_path"
            :src="`/thumbnails/${photo.thumbnail_path}`"
            :alt="photo.file_name"
          />
          <p class="compare-name">{{ photo.file_name }}</p>
          <p class="compare-size">{{ formatSize(photo.file_size) }}</p>
        </div>
      </div>
      <template #footer>
        <button class="pill-btn" @click="compareVisible = false">关闭</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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

// 清理确认
const confirmVisible = ref(false)
const confirmPhotos = ref<PhotoBrief[]>([])
const confirmCount = ref(0)
const confirmSize = ref('')
const cleaning = ref(false)
let pendingCleanGroup: DupGroup | null = null

// 统计
const totalDuplicates = computed(() => {
  return groups.value.reduce((sum, g) => sum + Math.max(0, g.photos.length - 1), 0)
})

const totalGroups = computed(() => groups.value.length)

const totalWasteSize = computed(() => {
  return groups.value.reduce((sum, g) => {
    if (g.type === 'bitwise' && g.photos.length > 1) {
      // 保留第一张，其余算浪费
      return sum + g.photos.slice(1).reduce((s, p) => s + p.file_size, 0)
    }
    return sum
  }, 0)
})

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

function confirmClean(group: DupGroup) {
  const toDelete = group.photos.slice(1)
  pendingCleanGroup = group
  confirmPhotos.value = toDelete
  confirmCount.value = toDelete.length
  confirmSize.value = formatSize(toDelete.reduce((s, p) => s + p.file_size, 0))
  confirmVisible.value = true
}

async function doClean() {
  if (!pendingCleanGroup) return
  cleaning.value = true
  try {
    const toDelete = pendingCleanGroup.photos.slice(1)
    for (const photo of toDelete) {
      await (await import('@/api/photos')).deletePhotoFile(photo.id)
    }
    confirmVisible.value = false
    fetchGroups()
  } catch {
    // ignore
  } finally {
    cleaning.value = false
    pendingCleanGroup = null
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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
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
  align-items: center;
  gap: var(--space-3);
}

/* ===== 统计栏 ===== */
.stats-bar {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  padding: var(--space-4) var(--space-5);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.stat-value--highlight {
  color: var(--accent);
}

.stat-value--danger {
  color: var(--danger-500);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--border-color);
}

.dup-loading { padding: var(--space-6); }

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
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: box-shadow 200ms var(--ease-standard);
  animation: stagger-in 0.35s var(--ease-standard) backwards;
}

.dup-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.dup-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.dup-card-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dup-type-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: 12px;
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

.dup-count {
  font-size: 13px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.dup-action-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-caption);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dup-action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.dup-action-btn--danger {
  color: var(--danger-500);
  border-color: var(--danger-100);
}

.dup-action-btn--danger:hover {
  background: var(--danger-100);
  border-color: var(--danger-500);
}

.dup-photos-row {
  display: flex;
  gap: var(--space-3);
  overflow-x: auto;
  padding-bottom: var(--space-1);
}

.dup-photo-item {
  cursor: pointer;
  border-radius: var(--radius-md);
  overflow: hidden;
  width: 160px;
  flex-shrink: 0;
  background: var(--gray-100);
  border: 2px solid transparent;
  transition: all 200ms var(--ease-standard);
}

.dup-photo-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.dup-photo-item.is-original {
  border-color: var(--success-500);
}

.dup-photo-item.is-duplicate {
  border-color: var(--warning-500);
}

.dup-photo-thumb {
  position: relative;
  height: 120px;
}

.dup-photo-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.dup-photo-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
}

.photo-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: var(--font-weight-semibold);
}

.photo-badge--original {
  background: var(--success-500);
  color: white;
}

.photo-badge--dup {
  background: var(--warning-500);
  color: white;
}

.dup-photo-info {
  padding: var(--space-2) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dup-photo-name {
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.dup-photo-size {
  font-size: 11px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

/* ===== 确认模态框 ===== */
.confirm-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) 0;
}

.confirm-icon {
  color: var(--warning-500);
  opacity: 0.8;
}

.confirm-title {
  margin: 0;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.confirm-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
}

.confirm-preview {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  justify-content: center;
}

.confirm-thumb {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--gray-100);
}

.confirm-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ===== 对比对话框 ===== */
.compare-row {
  display: flex;
  gap: var(--space-6);
  justify-content: center;
  flex-wrap: wrap;
}

.compare-item {
  text-align: center;
  max-width: 400px;
}

.compare-item img {
  max-width: 100%;
  max-height: 400px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.compare-name {
  margin-top: var(--space-2);
  font-size: var(--text-body);
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.compare-size {
  margin-top: 2px;
  font-size: var(--text-caption);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

:deep(.glass-dialog .el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.pill-btn--danger {
  background: var(--danger-500);
  color: white;
}

.pill-btn--danger:hover {
  background: #DC2626;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
