<template>
  <div class="view-people">
    <div class="page-header">
      <h2>人物</h2>
      <div class="header-actions">
        <el-button
          size="small"
          :loading="detecting"
          @click="onDetectFaces"
        >
          检测人脸
        </el-button>
        <el-button
          size="small"
          :loading="clustering"
          @click="onClusterFaces"
        >
          重新聚类
        </el-button>
        <el-button
          v-if="selectedIds.length > 1"
          type="primary"
          size="small"
          @click="onMerge"
        >
          合并选中 ({{ selectedIds.length }})
        </el-button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-area">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-area">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button @click="fetchClusters">重试</el-button>
        </template>
      </el-result>
    </div>

    <!-- Empty -->
    <div v-else-if="clusters.length === 0" class="empty-area">
      <el-icon :size="48" color="#ccc"><User /></el-icon>
      <p>尚未检测到人脸</p>
      <p class="text-secondary">点击"检测人脸"开始扫描照片中的人脸</p>
      <el-button type="primary" :loading="detecting" @click="onDetectFaces" style="margin-top: 16px">
        检测人脸
      </el-button>
    </div>

    <!-- Clusters grid -->
    <template v-else>
      <div class="cluster-count">共 {{ total }} 个人物</div>
      <div class="clusters-grid">
        <div
          v-for="cluster in clusters"
          :key="cluster.id"
          class="cluster-card"
          :class="{ 'is-selected': selectedIds.includes(cluster.id) }"
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
              <el-icon :size="32"><User /></el-icon>
            </div>
          </div>
          <div class="card-info">
            <span class="card-name">{{ cluster.name || '人物 ' + cluster.id }}</span>
            <span class="card-count">{{ cluster.face_count }} 张照片</span>
          </div>
          <div v-if="selectedIds.includes(cluster.id)" class="check-badge">
            <el-icon><Check /></el-icon>
          </div>
        </div>
      </div>

      <div v-if="hasMore" class="load-more">
        <el-button text :loading="loading" @click="loadMore">加载更多</el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Check } from '@element-plus/icons-vue'
import { getFaceClusters, detectFaces, clusterFaces, mergeFaceClusters } from '@/api/faces'
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
  height: calc(100vh - 52px);
  display: flex;
  flex-direction: column;
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.page-header h2 { margin: 0; }
.header-actions {
  display: flex;
  gap: 8px;
}
.loading-area, .error-area, .empty-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.text-secondary {
  color: var(--color-text-secondary, #999);
  font-size: 14px;
}
.cluster-count {
  font-size: 13px;
  color: var(--color-text-secondary, #999);
  margin-bottom: 12px;
  flex-shrink: 0;
}
.clusters-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, 150px);
  gap: 12px;
  justify-content: center;
  align-content: start;
  align-items: start;
  overflow-y: auto;
  padding: 4px 0;
}
.cluster-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px 16px;
  border-radius: 12px;
  background: var(--color-bg-primary, #fff);
  border: 1px solid var(--color-border, #eee);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  user-select: none;
}
.cluster-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.cluster-card.is-selected {
  border-color: var(--color-primary, #7EC8C8);
  background: var(--color-primary-light, #e6f7f7);
}
.card-avatar {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-bg-tertiary, #f0f0f0);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.card-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-placeholder {
  color: #ddd;
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
  font-size: 13px;
  font-weight: 600;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
.card-count {
  font-size: 11px;
  color: var(--color-text-secondary, #999);
}
.check-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-primary, #7EC8C8);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.load-more {
  text-align: center;
  padding: 12px;
  flex-shrink: 0;
}
</style>
