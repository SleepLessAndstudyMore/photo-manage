<template>
  <div class="view-people-detail">
    <!-- Loading -->
    <div v-if="loading" class="loading-area">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Error / Not found -->
    <div v-else-if="error" class="error-area">
      <el-result icon="error" title="加载失败" :sub-title="error">
        <template #extra>
          <el-button @click="router.back()">返回</el-button>
          <el-button @click="fetchDetail">重试</el-button>
        </template>
      </el-result>
    </div>

    <template v-else-if="cluster">
      <!-- Header -->
      <div class="detail-header">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <div class="header-main">
          <div class="header-avatar">
            <img
              v-if="cluster.cover_thumbnail"
              :src="'/thumbnails/' + cluster.cover_thumbnail"
              alt="头像"
            />
            <div v-else class="avatar-placeholder">
              <el-icon :size="40"><User /></el-icon>
            </div>
          </div>
          <div class="header-info">
            <div class="name-row">
              <span v-if="!editing" class="person-name" @click="startEdit">
                {{ cluster.name || '人物 ' + cluster.id }}
                <el-icon class="edit-icon"><EditPen /></el-icon>
              </span>
              <div v-else class="name-edit-row">
                <el-input
                  v-model="editName"
                  size="small"
                  maxlength="32"
                  ref="nameInputRef"
                  @keyup.enter="saveName"
                />
                <el-button size="small" type="primary" @click="saveName">保存</el-button>
                <el-button size="small" @click="editing = false">取消</el-button>
              </div>
            </div>
            <span class="person-count">{{ cluster.face_count }} 张照片</span>
          </div>
          <div class="header-actions">
            <el-button size="small" @click="showSplitDialog = true">
              拆分
            </el-button>
          </div>
        </div>
      </div>

      <!-- Split dialog -->
      <el-dialog v-model="showSplitDialog" title="拆分人物" width="500px">
        <p class="split-hint">选择要拆分到新人物的人脸：</p>
        <div class="face-grid">
          <div
            v-for="face in cluster.faces"
            :key="face.id"
            class="face-item"
            :class="{ selected: splitFaceIds.includes(face.id) }"
            @click="toggleSplitFace(face.id)"
          >
            <img
              v-if="face.thumbnail_path"
              :src="'/thumbnails/' + face.thumbnail_path"
              alt="face"
            />
            <div v-else class="face-placeholder">
              <el-icon><User /></el-icon>
            </div>
            <div class="face-confidence">{{ (face.confidence * 100).toFixed(0) }}%</div>
          </div>
        </div>
        <template #footer>
          <el-button @click="showSplitDialog = false">取消</el-button>
          <el-button
            type="primary"
            :disabled="splitFaceIds.length === 0"
            :loading="splitting"
            @click="onSplit"
          >
            拆分为新人物 ({{ splitFaceIds.length }})
          </el-button>
        </template>
      </el-dialog>

      <!-- Photos -->
      <div class="photos-section">
        <div v-if="photosLoading" class="loading-area">
          <el-skeleton :rows="2" animated />
        </div>
        <div v-else-if="photos.length === 0" class="empty-area">
          <p>该人物暂无照片</p>
        </div>
        <template v-else>
          <div class="photos-header">
            <span>共 {{ photosTotal }} 张照片</span>
          </div>
          <div class="photos-grid">
            <div
              v-for="photo in photos"
              :key="photo.id"
              class="photo-item"
              @click="goToPhoto(photo.id)"
            >
              <img
                v-if="photo.thumbnail_path"
                :src="'/thumbnails/' + photo.thumbnail_path"
                :alt="photo.file_name"
                loading="lazy"
              />
              <div v-else class="photo-placeholder">
                <el-icon><PictureFilled /></el-icon>
              </div>
              <div class="photo-name">{{ photo.file_name }}</div>
            </div>
          </div>
          <div v-if="photosHasMore" class="load-more">
            <el-button text :loading="photosLoading" @click="loadMorePhotos">加载更多</el-button>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { ArrowLeft, EditPen, User, PictureFilled } from '@element-plus/icons-vue'
import { getFaceClusterDetail, getFaceClusterPhotos, updateFaceCluster, splitFaceCluster } from '@/api/faces'
import type { FaceClusterDetail } from '@/types/face'

const router = useRouter()
const route = useRoute()
const clusterId = Number(route.params.id)

const cluster = ref<FaceClusterDetail | null>(null)
const loading = ref(false)
const error = ref('')

const editing = ref(false)
const editName = ref('')
const nameInputRef = ref<HTMLInputElement>()

const showSplitDialog = ref(false)
const splitFaceIds = ref<number[]>([])
const splitting = ref(false)

const photos = ref<any[]>([])
const photosTotal = ref(0)
const photosLoading = ref(false)
const photosPage = ref(1)

onMounted(() => {
  fetchDetail()
  fetchPhotos()
})

async function fetchDetail() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await getFaceClusterDetail(clusterId)
    cluster.value = data
  } catch {
    error.value = '人物不存在或加载失败'
  } finally {
    loading.value = false
  }
}

async function fetchPhotos() {
  photosLoading.value = true
  try {
    const { data } = await getFaceClusterPhotos(clusterId, { page: 1, page_size: 50 })
    photos.value = data.items ?? []
    photosTotal.value = data.total ?? 0
    photosPage.value = 1
  } catch {
    // ignore
  } finally {
    photosLoading.value = false
  }
}

async function loadMorePhotos() {
  if (photosLoading.value) return
  photosPage.value++
  photosLoading.value = true
  try {
    const { data } = await getFaceClusterPhotos(clusterId, { page: photosPage.value, page_size: 50 })
    photos.value.push(...(data.items ?? []))
  } catch {
    photosPage.value--
  } finally {
    photosLoading.value = false
  }
}

const photosHasMore = computed(() => photos.value.length < photosTotal.value)

function startEdit() {
  editName.value = cluster.value?.name || ''
  editing.value = true
  nextTick(() => nameInputRef.value?.focus())
}

async function saveName() {
  if (!cluster.value) return
  try {
    await updateFaceCluster(clusterId, { name: editName.value })
    cluster.value.name = editName.value
    editing.value = false
  } catch {
    // ignore
  }
}

function toggleSplitFace(id: number) {
  const idx = splitFaceIds.value.indexOf(id)
  if (idx >= 0) {
    splitFaceIds.value.splice(idx, 1)
  } else {
    splitFaceIds.value.push(id)
  }
}

async function onSplit() {
  if (splitFaceIds.value.length === 0 || !cluster.value) return
  splitting.value = true
  try {
    await splitFaceCluster(clusterId, { face_ids: splitFaceIds.value })
    showSplitDialog.value = false
    splitFaceIds.value = []
    await fetchDetail()
    await fetchPhotos()
  } finally {
    splitting.value = false
  }
}

function goToPhoto(id: number) {
  router.push(`/photos/${id}`)
}

</script>

<style scoped>
.view-people-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--space-lg);
  overflow-y: auto;
}
.loading-area, .error-area, .empty-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
}
.detail-header {
  flex-shrink: 0;
  margin-bottom: var(--space-lg);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
}
.header-main {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-top: var(--space-md);
}
.header-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--bg-tertiary, #eee);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.header-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-placeholder {
  color: #ccc;
}
.header-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.name-row {
  display: flex;
  align-items: center;
}
.person-name {
  font-size: var(--text-2xl);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.edit-icon {
  font-size: var(--text-base);
  color: var(--text-secondary, #999);
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.person-name:hover .edit-icon {
  opacity: 1;
}
.name-edit-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.person-count {
  font-size: var(--text-base);
  color: var(--text-secondary, #999);
}
.header-actions {
  flex-shrink: 0;
}
.photos-section {
  flex: 1;
  overflow-y: auto;
}
.photos-header {
  font-size: var(--text-sm);
  color: var(--text-secondary, #999);
  margin-bottom: var(--space-md);
}
.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-md);
}
.photo-item {
  cursor: pointer;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-secondary, #f5f5f5);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}
.photo-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}
.photo-item img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}
.photo-placeholder {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}
.photo-name {
  padding: 6px 8px;
  font-size: var(--text-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.load-more {
  text-align: center;
  padding: var(--space-md);
}
/* Split dialog */
.split-hint {
  margin-bottom: var(--space-md);
  color: var(--text-secondary, #666);
}
.face-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}
.face-item {
  cursor: pointer;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 2px solid transparent;
  text-align: center;
  background: var(--bg-secondary, #f5f5f5);
  padding: 4px;
  transition: all var(--transition-fast);
}
.face-item.selected {
  border-color: var(--accent);
  box-shadow: var(--card-shadow);
}
.face-item img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--radius-sm);
}
.face-placeholder {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}
.face-confidence {
  font-size: var(--text-sm);
  color: var(--text-secondary, #999);
  margin-top: 2px;
}
</style>
