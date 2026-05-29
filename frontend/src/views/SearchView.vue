<template>
  <div class="view-search">
    <div class="search-toolbar">
      <div class="toolbar-top">
        <h2 class="page-title">搜索</h2>
        <SegmentedControl
          v-model="searchMode"
          :options="[
            { label: '结构化搜索', value: 'structured' },
            { label: '自然语言', value: 'hybrid' },
          ]"
        />
      </div>

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
            @blur="handleBlur"
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

        <!-- 搜索历史 -->
        <div v-if="showHistory && searchHistory.length > 0" class="search-history">
          <div class="history-header">
            <span class="history-label">最近搜索</span>
            <button class="history-clear" @click="clearHistory">清除全部</button>
          </div>
          <div class="history-list">
            <button
              v-for="item in searchHistory"
              :key="item"
              class="history-item"
              @click="hybridQuery = item; doSearch(); showHistory = false"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <span>{{ item }}</span>
            </button>
          </div>
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
        <div class="filter-row filter-row-primary">
          <div class="filter-field filter-name">
            <input v-model="structuredFilters.file_name" type="text" placeholder="文件名" />
          </div>
          <div class="filter-field filter-date">
            <el-date-picker v-model="structuredFilters.date_from" type="date" value-format="YYYY-MM-DD" placeholder="日期从" size="default" />
          </div>
          <div class="filter-field filter-date">
            <el-date-picker v-model="structuredFilters.date_to" type="date" value-format="YYYY-MM-DD" placeholder="日期至" size="default" />
          </div>
          <div class="filter-field filter-tags">
            <el-select v-model="structuredFilters.tag_ids" multiple clearable collapse-tags placeholder="标签" style="width: 100%">
              <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name_zh || tag.name" :value="tag.id" />
            </el-select>
          </div>
          <button class="filter-toggle" @click="showMoreFilters = !showMoreFilters">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" :style="{ transform: showMoreFilters ? 'rotate(180deg)' : '' }">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
            {{ showMoreFilters ? '收起' : '更多筛选' }}
          </button>
        </div>

        <!-- 展开的高级筛选 -->
        <Transition name="expand">
          <div v-show="showMoreFilters" class="filter-row filter-row-more">
            <div class="filter-field">
              <input v-model="structuredFilters.camera_model" type="text" placeholder="相机型号" />
            </div>
            <div class="filter-field">
              <input v-model="structuredFilters.lens_model" type="text" placeholder="镜头" />
            </div>
            <div class="filter-field">
              <el-rate v-model="structuredFilters.rating_min" :max="5" />
            </div>
            <div class="filter-field filter-switch-inline">
              <el-switch v-model="structuredFilters.is_favorite" />
              <span>仅收藏</span>
            </div>
            <el-radio-group v-model="structuredFilters.logic" size="small">
              <el-radio-button value="AND">与</el-radio-button>
              <el-radio-button value="OR">或</el-radio-button>
            </el-radio-group>
          </div>
        </Transition>

        <div class="filter-row filter-row-bottom">
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

      <EmptyState
        v-else-if="results.length === 0"
        type="search"
        title="未找到匹配的照片"
        subtitle="试试其他关键词"
      />

      <template v-else>
        <div class="results-divider" />
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
            <div v-if="searchMode === 'hybrid' && photo.similarity_score != null" class="result-info">
              <span class="result-score">
                {{ (photo.similarity_score * 100).toFixed(0) }}%
              </span>
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
import EmptyState from '@/components/EmptyState.vue'

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
const showMoreFilters = ref(false)

// 搜索历史
const STORAGE_KEY = 'photo_search_history'
const searchHistory = ref<string[]>([])
const showHistory = ref(false)

function loadHistory() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      searchHistory.value = JSON.parse(saved)
    }
  } catch { /* ignore */ }
}

function saveToHistory(query: string) {
  if (!query.trim()) return
  const trimmed = query.trim()
  searchHistory.value = [trimmed, ...searchHistory.value.filter(h => h !== trimmed)].slice(0, 5)
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(searchHistory.value))
  } catch { /* ignore */ }
}

function clearHistory() {
  searchHistory.value = []
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch { /* ignore */ }
}

function handleBlur() {
  // 延迟关闭，让点击历史项有时间触发
  setTimeout(() => {
    hybridFocused.value = false
    showHistory.value = false
  }, 200)
}

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
  loadHistory()
  try {
    const { data } = await getTags({ page_size: 200 })
    allTags.value = data.items ?? []
  } catch { /* ignore */ }
})

async function doSearch() {
  searching.value = true
  searched.value = true
  currentPage.value = 1
  showHistory.value = false

  if (searchMode.value === 'hybrid' && hybridQuery.value.trim()) {
    saveToHistory(hybridQuery.value)
  }

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
}

/* ===== 顶部工具栏 ===== */
.search-toolbar {
  flex-shrink: 0;
  padding: var(--space-6);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
}

.toolbar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.page-title {
  margin: 0;
  font-size: var(--text-h1);
  font-weight: var(--font-weight-bold);
  letter-spacing: var(--tracking-tight);
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
  border-radius: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  height: 44px;
}

.search-input-wrapper.focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.search-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: var(--text-placeholder);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 15px;
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
  border-radius: 8px;
  border: none;
  background: var(--brand-gradient);
  color: #fff;
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 56px;
  box-shadow: 0 2px 8px var(--brand-glow);
}

.search-submit:hover:not(:disabled) {
  background: var(--brand-gradient-hover);
  box-shadow: 0 4px 12px var(--brand-glow-strong);
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

/* ===== 搜索历史 ===== */
.search-history {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  margin-top: var(--space-1);
  box-shadow: var(--shadow-md);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.history-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.history-clear {
  font-size: 12px;
  color: var(--text-placeholder);
  background: none;
  border: none;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.history-clear:hover {
  color: var(--accent);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.history-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-body);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.history-item:hover {
  background: var(--gray-50);
  color: var(--text-primary);
}

.history-item svg {
  flex-shrink: 0;
  color: var(--text-placeholder);
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
  gap: var(--space-3);
}

.filter-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  align-items: center;
}

.filter-row-primary {
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

.filter-name {
  flex: 1.5;
  min-width: 200px;
}

.filter-date {
  flex: 0 1 auto;
  min-width: 150px;
}

.filter-tags {
  flex: 1.5;
  min-width: 200px;
}

.filter-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-caption);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.filter-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.filter-toggle svg {
  transition: transform 0.2s var(--ease-standard);
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s var(--ease-standard);
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  margin-bottom: 0;
  padding-top: 0;
  padding-bottom: 0;
}
.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 80px;
}

.filter-row-more {
  padding: var(--space-3);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.filter-switch-inline {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-body);
  color: var(--text-secondary);
  min-width: auto;
  flex: 0 0 auto;
}

.filter-row-bottom {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-top: var(--space-1);
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
  padding: 0 var(--space-6);
}

.results-placeholder, .results-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  gap: var(--space-4);
}

.results-divider {
  height: 1px;
  background: var(--border-color);
  margin: var(--space-4) 0;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  flex-shrink: 0;
}

.results-count {
  font-size: 14px;
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
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-card);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform 0.2s var(--ease-standard), box-shadow 0.2s var(--ease-standard);
  animation: stagger-in 0.35s var(--ease-standard) backwards;
}

.result-card:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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
  padding: var(--space-1) var(--space-3);
  position: absolute;
  bottom: var(--space-2);
  right: var(--space-2);
}

.result-score {
  font-size: 10px;
  color: #fff;
  background: var(--accent);
  padding: 2px var(--space-2);
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

[data-theme="dark"] .search-history {
  background: var(--bg-card);
}

[data-theme="dark"] .history-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

[data-theme="dark"] .filter-row-more {
  background: rgba(255, 255, 255, 0.02);
}
</style>
