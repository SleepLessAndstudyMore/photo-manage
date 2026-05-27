<template>
  <div class="view-tags">
    <div class="tags-header">
      <div class="tags-header-actions">
        <SegmentedControl
          v-model="tagType"
          :options="[
            { label: '全部', value: '' },
            { label: 'AI 标签', value: 'auto' },
            { label: '手动标签', value: 'manual' },
          ]"
          @update:modelValue="fetchTagList()"
        />
        <button class="pill-btn pill-btn--primary" @click="showAddTagDialog = true">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          创建标签
        </button>
      </div>
    </div>

    <div v-if="loading" class="tags-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="tags.length === 0" class="tags-empty">
      <div class="empty-icon-float">
        <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" />
        </svg>
      </div>
      <p>暂无标签</p>
      <p class="text-secondary">扫描照片后将自动生成 AI 标签</p>
    </div>

    <div v-else class="tag-cloud">
      <div
        v-for="(tag, index) in tags"
        :key="tag.id"
        class="tag-capsule"
        :style="{
          fontSize: tagFontSize(tag.photo_count),
          animationDelay: `${Math.min(index * 25, 400)}ms`
        }"
        @click="selectTag(tag)"
      >
        <span class="tag-name">{{ tag.name_zh || tag.name }}</span>
        <span class="tag-count">{{ tag.photo_count }}</span>
      </div>
    </div>

    <!-- Tag photos dialog -->
    <el-dialog
      v-model="tagDialogVisible"
      :title="selectedTag?.name_zh || selectedTag?.name"
      width="80%"
      top="5vh"
      class="glass-dialog"
    >
      <div v-if="tagPhotos.length === 0" class="dialog-empty">该标签下暂无照片</div>
      <div v-else class="tag-photos-grid">
        <div
          v-for="(photo, index) in tagPhotos"
          :key="photo.id"
          class="tag-photo-item"
          :style="{ animationDelay: `${Math.min(index * 30, 300)}ms` }"
          @click="goToPhoto(photo.id)"
        >
          <img
            v-if="photo.thumbnail_path"
            :src="`/thumbnails/${photo.thumbnail_path}`"
            :alt="photo.file_name"
          />
          <div v-else class="photo-placeholder">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
            </svg>
          </div>
        </div>
      </div>
      <template #footer>
        <button class="pill-btn" @click="tagDialogVisible = false">关闭</button>
      </template>
    </el-dialog>

    <!-- Create tag dialog -->
    <el-dialog v-model="showAddTagDialog" title="创建标签" width="400px" class="glass-dialog">
      <el-form label-position="top">
        <el-form-item label="英文名称">
          <el-input v-model="newTagName" placeholder="如: beautiful_landscape" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="newTagNameZh" placeholder="如: 美丽风景" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="pill-btn" @click="showAddTagDialog = false">取消</button>
        <button class="pill-btn pill-btn--primary" @click="handleCreateTag">创建</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTags, getTagPhotos, createTag } from '@/api/tags'
import SegmentedControl from '@/components/SegmentedControl.vue'

interface TagItem {
  id: number
  name: string
  name_zh: string | null
  type: string
  photo_count: number
}

interface PhotoItem {
  id: number
  file_name: string
  thumbnail_path: string | null
}

const router = useRouter()

const tags = ref<TagItem[]>([])
const loading = ref(false)
const tagType = ref('')
const tagDialogVisible = ref(false)
const selectedTag = ref<TagItem | null>(null)
const tagPhotos = ref<PhotoItem[]>([])
const showAddTagDialog = ref(false)
const newTagName = ref('')
const newTagNameZh = ref('')

const MAX_FONT_SIZE = 28
const MIN_FONT_SIZE = 13

onMounted(() => {
  fetchTagList()
})

async function fetchTagList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { sort_by: 'photo_count', page_size: 200 }
    if (tagType.value) params.type = tagType.value
    const { data } = await getTags(params)
    tags.value = data.items ?? []
  } finally {
    loading.value = false
  }
}

function tagFontSize(count: number) {
  if (tags.value.length === 0) return `${MIN_FONT_SIZE}px`
  const maxCount = Math.max(...tags.value.map(t => t.photo_count), 1)
  const ratio = count / maxCount
  return `${MIN_FONT_SIZE + ratio * (MAX_FONT_SIZE - MIN_FONT_SIZE)}px`
}

async function selectTag(tag: TagItem) {
  selectedTag.value = tag
  tagDialogVisible.value = true
  try {
    const { data } = await getTagPhotos(tag.id, { page_size: 200 })
    tagPhotos.value = data.items ?? []
  } catch {
    tagPhotos.value = []
  }
}

function goToPhoto(id: number) {
  router.push(`/photos/${id}`)
}

async function handleCreateTag() {
  if (!newTagName.value.trim()) return
  await createTag({ name: newTagName.value.trim(), name_zh: newTagNameZh.value.trim() || undefined })
  newTagName.value = ''
  newTagNameZh.value = ''
  showAddTagDialog.value = false
  fetchTagList()
}
</script>

<style scoped>
.view-tags {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--space-xl);
  overflow: hidden;
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  flex-shrink: 0;
}

.tags-header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.tags-loading {
  padding: var(--space-xl);
}

.tags-empty {
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

/* ===== 标签云 — 漂浮胶囊 ===== */
.tag-cloud {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 12px 16px;
  padding: var(--space-lg);
  overflow-y: auto;
}

.tag-capsule {
  cursor: pointer;
  padding: 8px 18px;
  border-radius: 100px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  box-shadow: var(--shadow-sm);
  transition: all 220ms cubic-bezier(0.22, 1, 0.36, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  line-height: 1.4;
  white-space: nowrap;
  animation: stagger-in 0.5s var(--ease-apple) both;
}

[data-theme="dark"] .tag-capsule {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.1);
}

.tag-capsule:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: var(--shadow-md), 0 0 20px var(--accent-glow);
  border-color: var(--accent);
  background: var(--accent-light);
}

.tag-name {
  font-weight: 500;
  color: var(--text-primary);
}

.tag-count {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

/* ===== Dialogs ===== */
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

:deep(.el-dialog__header) {
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-dialog__body) {
  padding: var(--space-xl);
}

:deep(.el-dialog__footer) {
  padding: var(--space-lg) var(--space-xl);
  border-top: 1px solid var(--border-color);
}

.tag-photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.tag-photo-item {
  cursor: pointer;
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  aspect-ratio: 1;
  background: var(--bg-secondary);
  box-shadow: var(--card-shadow);
  transition: all 220ms var(--ease-apple);
  animation: stagger-in 0.4s var(--ease-apple) both;
}

.tag-photo-item:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-3px) scale(1.02);
}

.tag-photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.dialog-empty {
  text-align: center;
  padding: var(--space-xl);
  color: var(--text-secondary);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
</style>
