<template>
  <div class="view-tags">
    <div class="tags-header">
      <h2 class="page-title">标签</h2>
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
      </div>
    </div>

    <div class="tags-search">
      <div class="search-input-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索标签..."
        />
      </div>
    </div>

    <div v-if="loading" class="tags-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <EmptyState
      v-else-if="filteredTags.length === 0"
      type="tags"
      title="暂无标签"
      subtitle="为照片添加标签，快速分类查找"
    />

    <div v-else class="tags-content"
    >
      <div
        v-for="(group, groupName) in groupedTags"
        :key="groupName"
        class="tag-group"
      >
        <div class="group-header"
        >
          <div class="group-header-left"
          >
            <div class="group-accent-line" />
            <h3 class="group-title">{{ groupName }}</h3>
          </div>
          <span class="group-count">{{ group.length }}</span>
        </div>
        <div class="tag-grid"
        >
          <div
            v-for="(tag, index) in group"
            :key="tag.id"
            class="tag-card"
            :class="{ 'is-empty': tag.photo_count === 0 }"
            :style="{ animationDelay: `${Math.min(index * 25, 400)}ms` }"
            @click="selectTag(tag)"
          >
            <div class="tag-dot" :style="{ backgroundColor: getTagColor(tag.name) }" />
            <div class="tag-card-info"
            >
              <span class="tag-name">{{ tag.name_zh || tag.name }}</span>
              <span class="tag-count">{{ tag.photo_count > 0 ? `${tag.photo_count} 张` : '—' }}</span>
            </div>
            <svg class="tag-arrow" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </div>
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

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTags, getTagPhotos } from '@/api/tags'
import SegmentedControl from '@/components/SegmentedControl.vue'
import EmptyState from '@/components/EmptyState.vue'

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
const searchQuery = ref('')
const tagDialogVisible = ref(false)
const selectedTag = ref<TagItem | null>(null)
const tagPhotos = ref<PhotoItem[]>([])

const MAX_FONT_SIZE = 28
const MIN_FONT_SIZE = 13

const filteredTags = computed(() => {
  if (!searchQuery.value) return tags.value
  const query = searchQuery.value.toLowerCase()
  return tags.value.filter(tag =>
    (tag.name_zh || tag.name).toLowerCase().includes(query) ||
    tag.name.toLowerCase().includes(query)
  )
})

const groupedTags = computed(() => {
  const groups: Record<string, TagItem[]> = {
    '人物': [],
    '场景': [],
    '物品': [],
    '其他': [],
  }

  filteredTags.value.forEach(tag => {
    const name = (tag.name_zh || tag.name).toLowerCase()
    if (name.includes('人') || name.includes('男') || name.includes('女') || name.includes('孩') || name.includes('老人')) {
      groups['人物'].push(tag)
    } else if (name.includes('海') || name.includes('山') || name.includes('城市') || name.includes('日落') || name.includes('风景')) {
      groups['场景'].push(tag)
    } else if (name.includes('车') || name.includes('电视') || name.includes('手机') || name.includes('电脑')) {
      groups['物品'].push(tag)
    } else {
      groups['其他'].push(tag)
    }
  })

  // 移除空分组
  return Object.fromEntries(
    Object.entries(groups).filter(([, tags]) => tags.length > 0)
  )
})

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

function getTagColor(name: string): string {
  const colors = [
    '#6366F1', '#8B5CF6', '#EC4899', '#F43F5E',
    '#F97316', '#EAB308', '#22C55E', '#06B6D4',
    '#3B82F6', '#A855F7', '#D946EF', '#F59E0B',
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
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

</script>

<style scoped>
.view-tags {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--space-6);
  overflow: hidden;
}

.page-title {
  margin: 0;
  font-size: var(--text-h1);
  font-weight: var(--font-weight-bold);
  letter-spacing: var(--tracking-tight);
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  flex-shrink: 0;
}

.tags-header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.tags-search {
  margin-bottom: var(--space-4);
  flex-shrink: 0;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  height: 36px;
}

.search-input-wrapper:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.search-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: var(--text-placeholder);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: var(--text-body);
  color: var(--text-primary);
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--text-placeholder);
}

.tags-loading {
  padding: var(--space-6);
}

.tags-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  gap: var(--space-4);
}

.empty-icon-float {
  opacity: 0.3;
  animation: float 4s ease-in-out infinite;
}

.tags-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ===== 分类分组 ===== */
.tag-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-color);
}

.tag-group:last-child {
  border-bottom: none;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.group-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.group-accent-line {
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: var(--brand-gradient);
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}

.group-count {
  font-size: 12px;
  color: var(--text-placeholder);
  font-variant-numeric: tabular-nums;
  font-weight: 500;
}

/* ===== 标签网格 ===== */
.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-3);
}

/* ===== 标签卡片 ===== */
.tag-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 200ms var(--ease-standard);
  animation: stagger-in 0.35s var(--ease-standard) backwards;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.tag-card:hover {
  border-color: #D1D5DB;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.tag-card.is-empty {
  opacity: 0.5;
}

.tag-card.is-empty:hover {
  box-shadow: none;
  transform: none;
}

/* 标签代表色圆点 */
.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.tag-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-count {
  font-size: 12px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.tag-arrow {
  color: var(--text-placeholder);
  flex-shrink: 0;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 200ms var(--ease-standard);
}

.tag-card:hover .tag-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* ===== Dialogs ===== */
:deep(.glass-dialog .el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
}

:deep(.el-dialog__header) {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-dialog__body) {
  padding: var(--space-6);
}

:deep(.el-dialog__footer) {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-color);
}

.tag-photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-3);
}

.tag-photo-item {
  cursor: pointer;
  border-radius: var(--radius-xs);
  overflow: hidden;
  position: relative;
  aspect-ratio: 1;
  background: var(--gray-100);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  animation: stagger-in 0.4s var(--transition-normal) backwards;
}

.tag-photo-item:hover {
  box-shadow: var(--shadow-sm);
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
  color: var(--text-placeholder);
}

.dialog-empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
</style>
