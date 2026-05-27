<template>
  <div class="view-people">
    <div class="page-header">
      <h2 class="page-title">人物</h2>
      <div class="header-actions">
        <button class="pill-btn" :class="{ 'is-loading': detecting }" :disabled="detecting" @click="onDetectFaces">
          <span v-if="detecting" class="spinner-sm" />
          检测人脸
        </button>
        <button class="pill-btn" :class="{ 'is-loading': clustering }" :disabled="clustering" @click="onClusterFaces">
          <span v-if="clustering" class="spinner-sm" />
          重新聚类
        </button>
        <button
          v-if="selectedIds.length > 1"
          class="pill-btn pill-btn--primary"
          @click="onMerge"
        >
          合并选中 ({{ selectedIds.length }})
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-area">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-area">
      <p>{{ error }}</p>
      <button class="pill-btn pill-btn--primary" @click="fetchClusters">重试</button>
    </div>

    <!-- Empty -->
    <div v-else-if="clusters.length === 0" class="empty-area">
      <div class="empty-icon-float">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
        </svg>
      </div>
      <p class="empty-title">尚未检测到人脸</p>
      <p class="text-secondary">点击下方按钮开始扫描照片中的人脸</p>
      <button class="pill-btn pill-btn--primary" style="margin-top: 16px" :disabled="detecting" @click="onDetectFaces">
        检测人脸
      </button>
    </div>

    <!-- Clusters grid -->
    <template v-else>
      <div class="cluster-count">共 {{ total }} 个人物</div>
      <div class="clusters-grid">
        <div
          v-for="(cluster, index) in clusters"
          :key="cluster.id"
          class="cluster-card"
          :class="{ 'is-selected': selectedIds.includes(cluster.id) }"
          :style="{ animationDelay: `${Math.min(index * 40, 400)}ms` }"
          @click="onSelect(cluster.id)"
          @dblclick="goToDetail(cluster.id)"
        >
          <div class="card-avatar">
            <img
              v-if="cluster.cover_thumbnail"
              :src="'/thumbnails/' + cluster.cover_thumbnail"
              :alt="cluster.name || '人物'"
            />
            <div v-else class="avatar-placeholder">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <!-- 编辑按钮 -->
            <button class="card-edit-btn" @click.stop="openRename(cluster)">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </button>
          </div>
          <div class="card-info">
            <span class="card-name">{{ cluster.name || '人物 ' + cluster.id }}</span>
            <span class="card-count">{{ cluster.face_count }} 张照片</span>
          </div>
          <div v-if="selectedIds.includes(cluster.id)" class="check-badge">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
        </div>
      </div>

      <div v-if="hasMore" class="load-more">
        <button class="pill-btn" :disabled="loading" @click="loadMore">加载更多</button>
      </div>
    </template>

    <!-- 重命名对话框 -->
    <el-dialog v-model="renameVisible" title="修改人物名称" width="360px" class="glass-dialog" @closed="renameName = ''">
      <div class="rename-preview">
        <img
          v-if="renameCluster?.cover_thumbnail"
          :src="'/thumbnails/' + renameCluster.cover_thumbnail"
          class="rename-avatar"
        />
        <div v-else class="rename-avatar-placeholder">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
          </svg>
        </div>
      </div>
      <el-input
        v-model="renameName"
        placeholder="输入人物名称"
        maxlength="64"
        show-word-limit
        clearable
        autofocus
        @keyup.enter="saveRename"
      />
      <template #footer>
        <button class="pill-btn" @click="renameVisible = false">取消</button>
        <button class="pill-btn pill-btn--primary" :disabled="!renameName.trim()" @click="saveRename">保存</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFaceClusters, detectFaces, clusterFaces, mergeFaceClusters, updateFaceCluster } from '@/api/faces'
import type { FaceCluster } from '@/types/face'

const router = useRouter()

const clusters = ref<FaceCluster[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref('')
const detecting = ref(false)
const clustering = ref(false)
const selectedIds = ref<number[]>([])
const currentPage = ref(1)

// 重命名
const renameVisible = ref(false)
const renameCluster = ref<FaceCluster | null>(null)
const renameName = ref('')

onMounted(() => {
  fetchClusters()
})

async function fetchClusters() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await getFaceClusters({ page: 1, page_size: 50 })
    clusters.value = data.items ?? []
    total.value = data.total ?? 0
    currentPage.value = 1
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (loading.value) return
  currentPage.value++
  loading.value = true
  try {
    const { data } = await getFaceClusters({ page: currentPage.value, page_size: 50 })
    clusters.value.push(...(data.items ?? []))
  } catch {
    currentPage.value--
  } finally {
    loading.value = false
  }
}

const hasMore = computed(() => clusters.value.length < total.value)

function onSelect(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}

async function onMerge() {
  if (selectedIds.value.length < 2) return
  try {
    await mergeFaceClusters({ cluster_ids: selectedIds.value })
    selectedIds.value = []
    await fetchClusters()
  } catch {
    // ignore
  }
}

function goToDetail(id: number) {
  router.push(`/people/${id}`)
}

function openRename(cluster: FaceCluster) {
  renameCluster.value = cluster
  renameName.value = cluster.name || ''
  renameVisible.value = true
}

async function saveRename() {
  if (!renameCluster.value || !renameName.value.trim()) return
  try {
    await updateFaceCluster(renameCluster.value.id, { name: renameName.value.trim() })
    renameCluster.value.name = renameName.value.trim()
    renameVisible.value = false
  } catch {
    // ignore
  }
}

async function onDetectFaces() {
  detecting.value = true
  try {
    await detectFaces()
  } finally {
    detecting.value = false
  }
}

async function onClusterFaces() {
  clustering.value = true
  try {
    await clusterFaces()
  } finally {
    clustering.value = false
  }
}
</script>

<style scoped>
.view-people {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--space-xl);
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: 200;
  letter-spacing: -1px;
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

.is-loading {
  opacity: 0.6;
}

.loading-area, .error-area, .empty-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
}

.empty-icon-float {
  color: var(--text-tertiary);
  opacity: 0.3;
  animation: float 4s ease-in-out infinite;
}

.empty-title {
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--text-secondary);
}

.text-secondary {
  color: var(--text-secondary);
  font-size: var(--text-base);
}

.cluster-count {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-bottom: var(--space-lg);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.clusters-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-lg);
  justify-content: center;
  align-content: start;
  overflow-y: auto;
  padding: var(--space-xs);
}

/* ===== 人物卡片 — Apple Photos 风格 ===== */
.cluster-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-xl) var(--space-md) var(--space-lg);
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-glass);
  box-shadow: var(--card-shadow);
  cursor: pointer;
  transition: all 220ms cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;
  user-select: none;
  animation: stagger-in 0.5s var(--ease-apple) both;
}

[data-theme="dark"] .cluster-card {
  background: rgba(255, 255, 255, 0.04);
}

.cluster-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--card-shadow-hover);
}

.cluster-card.is-selected {
  border-color: var(--accent);
  background: var(--accent-light);
  box-shadow: 0 0 24px var(--accent-glow);
}

.card-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: transform 0.4s var(--ease-apple);
}

.cluster-card:hover .card-avatar {
  transform: scale(1.08);
}

.card-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 编辑按钮 */
.card-edit-btn {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.2s var(--ease-apple);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] .card-edit-btn {
  background: rgba(50, 50, 54, 0.85);
}

.cluster-card:hover .card-edit-btn {
  opacity: 1;
  transform: scale(1);
}

.card-edit-btn:hover {
  background: var(--accent);
  color: #fff;
}

.avatar-placeholder {
  color: var(--text-tertiary);
  opacity: 0.4;
}

.card-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 0;
  width: 100%;
}

.card-name {
  font-size: var(--text-base);
  font-weight: 500;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.card-count {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.check-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
}

.load-more {
  text-align: center;
  padding: var(--space-md);
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* 重命名对话框 */
.rename-preview {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-lg);
}

.rename-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.rename-avatar-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
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
</style>
