<template>
  <div class="view-people">
    <div class="page-header">
      <h2 class="page-title">人物</h2>
      <div class="header-actions">
        <div class="action-group">
          <button class="action-btn" :class="{ 'is-loading': detecting }" :disabled="detecting" @click="onDetectFaces">
            <span v-if="detecting" class="spinner-sm" />
            <span class="action-btn-main">扫描人脸</span>
            <span class="action-btn-sub">自动识别照片中的人物</span>
          </button>
          <button class="action-btn" :class="{ 'is-loading': clustering }" :disabled="clustering" @click="onClusterFaces">
            <span v-if="clustering" class="spinner-sm" />
            <span class="action-btn-main">重新分组</span>
            <span class="action-btn-sub">合并或拆分人物分组</span>
          </button>
        </div>
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
    <EmptyState
      v-else-if="clusters.length === 0"
      type="people"
      title="尚未检测到人脸"
      subtitle="扫描照片中的人脸，自动按人物分组"
      action-text="开始扫描"
      @action="onDetectFaces"
    />

    <!-- Clusters grid -->
    <template v-else>
      <div class="cluster-section">
        <h3 class="section-title">已命名</h3>
        <div class="clusters-grid">
          <div
            v-for="(cluster, index) in namedClusters"
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
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <button class="card-edit-btn" @click.stop="openRename(cluster)">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
            </div>
            <div class="card-info">
              <span class="card-name">{{ cluster.name }}</span>
              <span class="card-count">{{ cluster.face_count }} 张照片</span>
            </div>
            <div v-if="selectedIds.includes(cluster.id)" class="check-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div v-if="unnamedClusters.length > 0" class="cluster-section">
        <h3 class="section-title">待命名</h3>
        <div class="clusters-grid">
          <div
            v-for="(cluster, index) in unnamedClusters"
            :key="cluster.id"
            class="cluster-card cluster-card--unnamed"
            :class="{ 'is-selected': selectedIds.includes(cluster.id) }"
            :style="{ animationDelay: `${Math.min(index * 40, 400)}ms` }"
            @click="onSelect(cluster.id)"
            @dblclick="goToDetail(cluster.id)"
          >
            <div class="card-avatar">
              <img
                v-if="cluster.cover_thumbnail"
                :src="'/thumbnails/' + cluster.cover_thumbnail"
                :alt="'人物'"
              />
              <div v-else class="avatar-placeholder">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <button class="card-edit-btn" @click.stop="openRename(cluster)">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
            </div>
            <div class="card-info">
              <span class="card-name card-name--placeholder" @click.stop="openRename(cluster)">添加姓名</span>
              <span class="card-count">{{ cluster.face_count }} 张照片</span>
            </div>
            <div v-if="selectedIds.includes(cluster.id)" class="check-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
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
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
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
import EmptyState from '@/components/EmptyState.vue'

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

const namedClusters = computed(() => clusters.value.filter(c => c.name))
const unnamedClusters = computed(() => clusters.value.filter(c => !c.name))

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
  padding: var(--space-6);
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
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
  gap: var(--space-3);
  align-items: center;
}

.action-group {
  display: flex;
  gap: var(--space-3);
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.action-btn-main {
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
}

.action-btn-sub {
  font-size: 11px;
  color: var(--text-placeholder);
  font-weight: var(--font-weight-regular);
}

.action-btn:hover .action-btn-sub {
  color: var(--accent);
  opacity: 0.7;
}

.pill-btn--ghost {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.pill-btn--ghost:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
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
  gap: var(--space-4);
}

.empty-icon-float {
  color: var(--text-placeholder);
  opacity: 0.3;
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

.cluster-section {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-overline);
  font-weight: var(--font-weight-semibold);
  color: var(--text-placeholder);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin: 0 0 var(--space-4);
}

.clusters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-4);
}

/* ===== 人物卡片 ===== */
.cluster-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s ease;
  position: relative;
  user-select: none;
  animation: stagger-in 0.4s var(--transition-normal) backwards;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.cluster-card:hover {
  border-color: var(--accent);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15), 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-6px) scale(1.02);
}

.cluster-card.is-selected {
  border-color: var(--accent);
  background: var(--accent-light);
}

.cluster-card--unnamed .card-name {
  color: var(--accent);
}

.card-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.cluster-card:hover .card-avatar {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 编辑按钮 */
.card-edit-btn {
  position: absolute;
  bottom: 44px;
  right: calc(50% - 52px);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--bg-card);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.8);
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
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
  color: var(--text-placeholder);
  opacity: 0.4;
}

.card-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 0;
  width: 100%;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  color: var(--text-primary);
}

.card-name--placeholder {
  color: var(--accent);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.card-name--placeholder:hover {
  opacity: 0.8;
}

.card-count {
  font-size: 12px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.check-badge {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px var(--brand-glow);
}

.load-more {
  text-align: center;
  padding: var(--space-4);
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
  margin-bottom: var(--space-4);
}

.rename-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: var(--shadow-sm);
}

.rename-avatar-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
}

:deep(.glass-dialog .el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
}
</style>
