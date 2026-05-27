<template>
  <div class="view-search">
    <!-- 顶部工具栏 -->
    <div class="search-toolbar">
      <SegmentedControl
        v-model="searchMode"
        :options="[
          { label: '结构化搜索', value: 'structured' },
          { label: '自然语言', value: 'hybrid' },
        ]"
      />

      <!-- Hybrid search bar -->
      <div v-if="searchMode === 'hybrid'" class="hybrid-toolbar">
        <div class="search-input-wrapper" :class="{ focused: hybridFocused }">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="hybridQuery"
            type="text"
            class="search-input"
            placeholder="描述你想找的照片，例如：去年在海边的猫..."
            @focus="hybridFocused = true"
            @blur="hybridFocused = false"
            @keyup.enter="doSearch"
          />
          <button v-if="hybridQuery" class="search-clear" @click="hybridQuery = ''">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <button class="search-submit" :disabled="!hybridQuery.trim() || searching" @click="doSearch">
            <span v-if="searching" class="spinner-sm" />
            <span v-else>搜索</span>
          </button>
        </div>
        <div class="hybrid-hints">
          <button class="hint-chip" @click="hybridQuery = '去年在海边的猫'">去年在海边的猫</button>
          <button class="hint-chip" @click="hybridQuery = '今年旅行'">今年旅行</button>
          <button class="hint-chip" @click="hybridQuery = '最近7天的照片'">最近7天</button>
        </div>
        <button class="pill-btn pill-btn--sm" :disabled="embeddingLoading" @click="onGenerateEmbeddings">
          {{ embeddingLoading ? '生成中...' : '生成向量' }}
        </button>
      </div>

      <!-- Structured filters -->
      <div v-else class="structured-toolbar">
        <div class="filter-row">
          <div class="filter-field">
            <input v-model="structuredFilters.file_name" type="text" placeholder="文件名" />
          </div>
          <div class="filter-field">
            <input v-model="structuredFilters.camera_model" type="text" placeholder="相机型号" />
          </div>
          <div class="filter-field">
            <input v-model="structuredFilters.lens_model" type="text" placeholder="镜头" />
          </div>
          <div class="filter-field filter-date">
            <el-date-picker v-model="structuredFilters.date_from" type="date" value-format="YYYY-MM-DD" placeholder="日期从" size="default" />
          </div>
          <div class="filter-field filter-date">
            <el-date-picker v-model="structuredFilters.date_to" type="date" value-format="YYYY-MM-DD" placeholder="日期至" size="default" />
          </div>
          <div class="filter-field filter-wide">
            <el-select v-model="structuredFilters.tag_ids" multiple clearable collapse-tags placeholder="标签" style="width: 100%">
              <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name_zh || tag.name" :value="tag.id" />
            </el-select>
          </div>
        </div>
        <div class="filter-row filter-row-bottom">
          <div class="filter-extras">
            <el-rate v-model="structuredFilters.rating_min" :max="5" />
            <div class="filter-switch">
              <el-switch v-model="structuredFilters.is_favorite" />
              <span>仅收藏</span>
            </div>
            <el-radio-group v-model="structuredFilters.logic" size="small">
              <el-radio-button value="AND">与</el-radio-button>
              <el-radio-button value="OR">或</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-btns">
            <button class="pill-btn pill-btn--primary" :disabled="searching" @click="doSearch">搜索</button>
            <button class="pill-btn" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search results -->
    <div class="search-results">
      <div v-if="!searched" class="results-placeholder">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <p>输入搜索条件开始查找照片</p>
      </div>

      <div v-else-if="searching" class="results-loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="results.length === 0" class="results-empty">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <p>未找到匹配的照片</p>
      </div>

      <template v-else>
        <div class="results-header">
          <span class="results-count">找到 {{ total }} 张照片</span>
          <SegmentedControl
            v-model="sortBy"
            :options="[
              { label: '日期', value: 'date_taken' },
              { label: '评分', value: 'rating' },
              { label: '名称', value: 'file_name' },
            ]"
            @update:modelValue="doSearch()"
          />
        </div>
        <div class="results-grid">
          <div
            v-for="(photo, index) in results"
            :key="photo.id"
            class="result-card"
            :style="{ animationDelay: `${Math.min(index * 30, 300)}ms` }"
            @click="goToPhoto(photo.id)"
          >
            <img
              v-if="photo.thumbnail_path"
              :src="`/thumbnails/${photo.thumbnail_path}`"
              :alt="photo.file_name"
              loading="lazy"
            />
            <div v-else class="result-placeholder">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <div class="result-info">
              <span class="result-name">{{ photo.file_name }}</span>
              <div class="result-meta">
                <span v-if="photo.date_taken" class="result-date">{{ formatDate(photo.date_taken) }}</span>
                <span v-if="searchMode === 'hybrid' && photo.similarity_score != null" class="result-score">
                  {{ (photo.similarity_score * 100).toFixed(0) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-if="hasMore" class="results-more">
          <button class="pill-btn" @click="loadMore">加载更多</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { searchPhotos, generateEmbeddings } from '@/api/photos'
import { getTags } from '@/api/tags'
import SegmentedControl from '@/components/SegmentedControl.vue'

interface PhotoItem {
  id: number
  file_name: string
  date_taken: string | null
  thumbnail_path: string | null
  similarity_score?: number
}

interface TagItem {
  id: number
  name: string
  name_zh: string | null
}

const router = useRouter()

const searchMode = ref<'structured' | 'hybrid'>('structured')
const hybridQuery = ref('')
const hybridFocused = ref(false)
const allTags = ref<TagItem[]>([])
const searching = ref(false)
const searched = ref(false)
const embeddingLoading = ref(false)
const results = ref<PhotoItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const sortBy = ref('date_taken')

const structuredFilters = reactive({
  file_name: '',
  camera_model: '',
  lens_model: '',
  date_from: null,
  date_to: null,
  tag_ids: [] as number[],
  rating_min: 0,
  is_favorite: false,
  logic: 'AND' as string,
})

onMounted(async () => {
  try {
    const { data } = await getTags({ page_size: 200 })
    allTags.value = data.items ?? []
  } catch { /* ignore */ }
  doSearch()
})

async function doSearch() {
  searching.value = true
  searched.value = true
  currentPage.value = 1

  try {
    let body: Record<string, unknown>

    if (searchMode.value === 'hybrid') {
      body = {
        mode: 'hybrid',
        query: hybridQuery.value,
        page: 1,
        page_size: 50,
      }
    } else {
      const filters: Record<string, unknown> = {}
      if (structuredFilters.file_name) filters.file_name = structuredFilters.file_name
      if (structuredFilters.camera_model) filters.camera_model = structuredFilters.camera_model
      if (structuredFilters.lens_model) filters.lens_model = structuredFilters.lens_model
      if (structuredFilters.date_from) filters.date_from = structuredFilters.date_from
      if (structuredFilters.date_to) filters.date_to = structuredFilters.date_to
      if (structuredFilters.tag_ids.length) filters.tag_ids = structuredFilters.tag_ids
      if (structuredFilters.rating_min > 0) filters.rating_min = structuredFilters.rating_min
      if (structuredFilters.is_favorite) filters.is_favorite = true

      body = {
        mode: 'structured',
        filters,
        logic: structuredFilters.logic,
        sort_by: sortBy.value,
        sort_order: 'desc',
        page: 1,
        page_size: 50,
      }
    }

    const { data } = await searchPhotos(body)
    results.value = data.items ?? []
    total.value = data.total ?? 0
  } catch {
    results.value = []
    total.value = 0
  } finally {
    searching.value = false
  }
}

function resetFilters() {
  structuredFilters.file_name = ''
  structuredFilters.camera_model = ''
  structuredFilters.lens_model = ''
  structuredFilters.date_from = null
  structuredFilters.date_to = null
  structuredFilters.tag_ids = []
  structuredFilters.rating_min = 0
  structuredFilters.is_favorite = false
  structuredFilters.logic = 'AND'
  searched.value = false
  results.value = []
}

const hasMore = computed(() => results.value.length < total.value)

async function loadMore() {
  if (searching.value) return
  currentPage.value++
  searching.value = true
  try {
    const body: Record<string, unknown> = {
      mode: searchMode.value,
      page: currentPage.value,
      page_size: 50,
    }
    if (searchMode.value === 'hybrid') {
      body.query = hybridQuery.value
    } else {
      body.filters = { ...structuredFilters }
      body.logic = structuredFilters.logic
      body.sort_by = sortBy.value
      body.sort_order = 'desc'
    }
    const { data } = await searchPhotos(body)
    results.value.push(...(data.items ?? []))
  } finally {
    searching.value = false
  }
}

async function onGenerateEmbeddings() {
  embeddingLoading.value = true
  try {
    await generateEmbeddings()
  } finally {
    embeddingLoading.value = false
  }
}

function goToPhoto(id: number) {
  router.push(`/photos/${id}`)
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.view-search {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== 顶部工具栏 ===== */
.search-toolbar {
  flex-shrink: 0;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
}

/* ===== Hybrid 搜索 ===== */
.hybrid-toolbar {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-2) var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}

.search-input-wrapper.focused {
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
  padding: var(--space-2) 0;
}

.search-input::placeholder {
  color: var(--text-placeholder);
}

.search-clear {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: var(--gray-100);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-clear:hover {
  background: var(--gray-200);
}

.search-submit {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  border: none;
  background: var(--accent);
  color: #fff;
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 56px;
}

.search-submit:hover:not(:disabled) {
  background: var(--accent-hover);
}

.search-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.hybrid-hints {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.hint-chip {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: var(--text-caption);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.hint-chip:hover {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--accent);
}

.pill-btn--sm {
  align-self: flex-start;
}

/* ===== 结构化筛选 ===== */
.structured-toolbar {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.filter-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  align-items: center;
}

.filter-field {
  flex: 1;
  min-width: 130px;
}

.filter-field input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  font-size: var(--text-body);
  color: var(--text-primary);
  font-family: inherit;
  outline: none;
  transition: border-color var(--transition-fast);
}

.filter-field input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.filter-wide {
  flex: 1.5;
  min-width: 180px;
}

.filter-date {
  flex: 0 1 auto;
  min-width: 150px;
}

.filter-row-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-1);
}

.filter-extras {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.filter-switch {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-body);
  color: var(--text-secondary);
}

.filter-btns {
  display: flex;
  gap: var(--space-2);
}

/* ===== 搜索结果 ===== */
.search-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: var(--space-4) var(--space-6);
}

.results-placeholder, .results-loading, .results-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  gap: var(--space-4);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  flex-shrink: 0;
}

.results-count {
  font-size: var(--text-caption);
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
  overflow-y: auto;
  flex: 1;
}

/* ===== 结果卡片 ===== */
.result-card {
  border-radius: var(--radius-xs);
  overflow: hidden;
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  cursor: pointer;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  animation: stagger-in 0.4s var(--transition-normal) both;
}

.result-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-sm);
}

.result-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.result-placeholder {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-100);
  color: var(--text-placeholder);
}

.result-info {
  padding: var(--space-2) var(--space-3);
}

.result-name {
  display: block;
  font-size: var(--text-caption);
  font-weight: var(--font-weight-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  margin-top: 2px;
}

.result-date {
  font-size: var(--text-caption);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.result-score {
  font-size: 10px;
  color: #fff;
  background: var(--accent);
  padding: 0 var(--space-2);
  border-radius: var(--radius-full);
  font-weight: var(--font-weight-semibold);
}

.results-more {
  text-align: center;
  padding: var(--space-4);
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
