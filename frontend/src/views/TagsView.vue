<template>
  <div class="view-tags">
    <div class="tags-header">
      <h2>标签云</h2>
      <div class="tags-header-actions">
        <el-radio-group v-model="tagType" size="small" @change="fetchTagList">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="auto">AI 标签</el-radio-button>
          <el-radio-button value="manual">手动标签</el-radio-button>
        </el-radio-group>
        <el-button size="small" text @click="showAddTagDialog = true">创建标签</el-button>
      </div>
    </div>

    <div v-if="loading" class="tags-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="tags.length === 0" class="tags-empty">
      <el-icon :size="48"><PriceTag /></el-icon>
      <p>暂无标签，扫描照片后将自动生成 AI 标签</p>
    </div>

    <div v-else class="tag-cloud">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="tag-item"
        :style="{ fontSize: tagFontSize(tag.photo_count) }"
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
    >
      <div v-if="tagPhotos.length === 0" class="dialog-empty">该标签下暂无照片</div>
      <div v-else class="tag-photos-grid">
        <div
          v-for="photo in tagPhotos"
          :key="photo.id"
          class="tag-photo-item"
          @click="goToPhoto(photo.id)"
        >
          <img
            v-if="photo.thumbnail_path"
            :src="`/thumbnails/${photo.thumbnail_path}`"
            :alt="photo.file_name"
          />
          <div v-else class="photo-placeholder">
            <el-icon><PictureFilled /></el-icon>
          </div>
          <div v-if="selectedTag?.type === 'auto'" class="photo-tag-info">
            <el-tag size="small" type="info">
              {{ selectedTag?.name_zh || selectedTag?.name }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="tagDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Create tag dialog -->
    <el-dialog v-model="showAddTagDialog" title="创建标签" width="400px">
      <el-form label-position="top">
        <el-form-item label="英文名称">
          <el-input v-model="newTagName" placeholder="如: beautiful_landscape" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="newTagNameZh" placeholder="如: 美丽风景" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddTagDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTag">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PriceTag, PictureFilled } from '@element-plus/icons-vue'
import { getTags, getTagPhotos, createTag } from '@/api/tags'

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

const MAX_FONT_SIZE = 36
const MIN_FONT_SIZE = 12

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
}
.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  flex-shrink: 0;
}
.tags-header h2 {
  margin: 0;
  font-size: var(--text-2xl);
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
  color: var(--text-secondary);
  gap: var(--space-md);
}
.tag-cloud {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: var(--space-md) var(--space-xl);
  padding: var(--space-lg);
  overflow-y: auto;
}
.tag-item {
  cursor: pointer;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--accent-light);
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  line-height: 1.4;
  white-space: nowrap;
}
.tag-item:hover {
  background: var(--accent);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}
.tag-count {
  font-size: var(--text-sm);
  opacity: 0.7;
}
.tag-photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-md);
}
.tag-photo-item {
  cursor: pointer;
  border-radius: var(--radius-md);
  overflow: hidden;
  position: relative;
  aspect-ratio: 1;
  background: var(--bg-secondary);
  box-shadow: var(--card-shadow);
  transition: all var(--transition-fast);
}
.tag-photo-item:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
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
.photo-tag-info {
  position: absolute;
  bottom: 6px;
  left: 6px;
}
.dialog-empty {
  text-align: center;
  padding: var(--space-xl);
  color: var(--text-secondary);
}

/* Dialog glassmorphism */
:deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
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
</style>
