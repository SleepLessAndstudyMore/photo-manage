<template>
  <div class="view-search">
    <!-- 搜索区 -->
    <div class="search-hero">
      <h2 class="search-title">搜索</h2>
      <div class="search-mode-tabs">
        <button
          class="mode-tab"
          :class="{ active: searchMode === 'structured' }"
          @click="searchMode = 'structured'"
        >
          结构化搜索
        </button>
        <button
          class="mode-tab"
          :class="{ active: searchMode === 'hybrid' }"
          @click="searchMode = 'hybrid'"
        >
          自然语言
        </button>
      </div>

      <!-- Hybrid search -->
      <div v-if="searchMode === 'hybrid'" class="hybrid-search-box">
        <div class="search-input-wrapper" :class="{ focused: hybridFocused }">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
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
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
          <button class="search-submit" :disabled="!hybridQuery.trim() || searching" @click="doSearch">
            <span v-if="searching" class="spinner-sm" />
            <span v-else>搜索</span>
          </button>
        </div>
        <div class="search-hints">
          <span class="hint-label">试试：</span>
          <button class="hint-chip" @click="hybridQuery = '去年在海边的猫'">去年在海边的猫</button>
          <button class="hint-chip" @click="hybridQuery = '今年旅行'">今年旅行</button>
          <button class="hint-chip" @click="hybridQuery = '最近7天的照片'">最近7天的照片</button>
        </div>
        <div class="search-actions">
          <button class="pill-btn" :loading="embeddingLoading" @click="onGenerateEmbeddings">
            生成向量
          </button>
        </div>
      </div>

      <!-- Structured search -->
      <div v-else class="structured-filters">
        <div class="filter-grid">
          <div class="filter-item">
            <label>文件名</label>
            <input v-model="structuredFilters.file_name" type="text" placeholder="模糊搜索" />
          </div>
          <div class="filter-item">
            <label>相机型号</label>
            <input v-model="structuredFilters.camera_model" type="text" placeholder="如: Sony A7M4" />
          </div>
          <div class="filter-item">
            <label>镜头</label>
            <input v-model="structuredFilters.lens_model" type="text" placeholder="如: FE 24-70mm" />
          </div>
          <div class="filter-item">
            <label>日期从</label>
            <el-date-picker v-model="structuredFilters.date_from" type="date" value-format="YYYY-MM-DD" size="default" />
          </div>
          <div class="filter-item">
            <label>日期至</label>
            <el-date-picker v-model="structuredFilters.date_to" type="date" value-format="YYYY-MM-DD" size="default" />
          </div>
          <div class="filter-item">
            <label>标签</label>
            <el-select v-model="structuredFilters.tag_ids" multiple clearable placeholder="选择标签" style="width: 100%">
              <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name_zh || tag.name" :value="tag.id" />
            </el-select>
          </div>
          <div class="filter-item">
            <label>最低评分</label>
            <el-rate v-model="structuredFilters.rating_min" :max="5" />
          </div>
          <div class="filter-item filter-actions">
            <el-switch v-model="structuredFilters.is_favorite" />
            <span class="switch-label">仅收藏</span>
            <el-radio-group v-model="structuredFilters.logic" size="small" style="margin-left: auto">
              <el-radio-button value="AND">与</el-radio-button>
              <el-radio-button value="OR">或</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="filter-bottom">
          <button class="pill-btn pill-btn--primary" :loading="searching" @click="doSearch">搜索</button>
          <button class="pill-btn" @click="resetFilters">重置</button>
        </div>
      </div>
    </div>

    <!-- Search results -->
    <div class="search-results">
      <div v-if="!searched" class="results-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
        <p>输入搜索条件开始查找照片</p>
      </div>

      <div v-else-if="searching" class="results-loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="results.length === 0" class="results-empty">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
        <p>未找到匹配的照片</p>
      </div>

      <template v-else>
        <div class="results-header">
          <span class="results-count">找到 {{ total }} 张照片</span>
          <div class="sort-tabs">
            <button class="sort-tab" :class="{ active: sortBy === 'date_taken' }" @click="sortBy = 'date_taken'; doSearch()">日期</button>
            <button class="sort-tab" :class="{ active: sortBy === 'rating' }" @click="sortBy = 'rating'; doSearch()">评分</button>
            <button class="sort-tab" :class="{ active: sortBy === 'file_name' }" @click="sortBy = 'file_name'; doSearch()">名称</button>
          </div>
        </div>
        <div class="results-grid">
          <div
            v-for="(photo, index) in results"
            :key="photo.id"
            class="result-card"
            :style="{ animationDelay: `${Math.min(index * 30, 300)}ms` }"
            @click="goToPhoto(photo.id)"
          >
            <div class="result-card-inner">
              <img
                v-if="photo.thumbnail_path"
                :src="`/thumbnails/${photo.thumbnail_path}`"
                :alt="photo.file_name"
                loading="lazy"
              />
              <div v-else class="result-placeholder">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
              <div class="result-overlay">
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

/* ===== 搜索 Hero 区 ===== */
.search-hero {
  padding: var(--space-xl) var(--space-xl) var(--space-lg);
  flex-shrink: 0;
}

.search-title {
  margin: 0 0 var(--space-lg);
  font-size: var(--text-3xl);
  font-weight: 200;
  letter-spacing: -1px;
  color: var(--text-primary);
}

.search-mode-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: var(--space-lg);
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
  padding: 3px;
  width: fit-content;
}

[data-theme="dark"] .search-mode-tabs {
  background: rgba(255, 255, 255, 0.06);
}

.mode-tab {
  padding: 7px 18px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mode-tab.active {
  background: var(--card-bg);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(12px);
}

/* ===== Hybrid 搜索框 ===== */
.hybrid-search-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 4px 4px 4px 18px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.search-input-wrapper.focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-light), var(--shadow-md);
}

[data-theme="dark"] .search-input-wrapper {
  background: rgba(255, 255, 255, 0.06);
}

.search-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: var(--text-tertiary);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: var(--text-base);
  color: var(--text-primary);
  font-family: inherit;
  padding: 10px 0;
}

.search-input::placeholder {
  color: var(--text-tertiary);
  font-weight: 300;
}

.search-clear {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-clear:hover {
  background: rgba(0, 0, 0, 0.1);
}

.search-submit {
  padding: 8px 20px;
  border-radius: 12px;
  border: none;
  background: var(--accent);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 64px;
}

.search-submit:hover:not(:disabled) {
  background: var(--accent-hover);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
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

.search-hints {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.hint-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.hint-chip {
  padding: 4px 12px;
  border-radius: 100px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
  backdrop-filter: blur(8px);
}

.hint-chip:hover {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--accent);
}

.search-actions {
  display: flex;
  gap: var(--space-sm);
}

/* ===== Structured filters ===== */
.structured-filters {
  padding: var(--space-lg);
  background: var(--card-bg);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-md);
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item label {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.filter-item input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.5);
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-family: inherit;
  outline: none;
  transition: border-color var(--transition-fast);
}

.filter-item input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

[data-theme="dark"] .filter-item input {
  background: rgba(255, 255, 255, 0.06);
}

.filter-actions {
  flex-direction: row;
  align-items: center;
  gap: var(--space-sm);
}

.switch-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.filter-bottom {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-color);
}

/* ===== 搜索结果 ===== */
.search-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 var(--space-xl) var(--space-xl);
}

.results-placeholder, .results-loading, .results-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  gap: var(--space-md);
}

.placeholder-icon {
  opacity: 0.3;
  animation: float 4s ease-in-out infinite;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  flex-shrink: 0;
}

.results-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

.sort-tabs {
  display: flex;
  gap: 2px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 8px;
  padding: 2px;
}

[data-theme="dark"] .sort-tabs {
  background: rgba(255, 255, 255, 0.06);
}

.sort-tab {
  padding: 5px 14px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sort-tab.active {
  background: var(--card-bg);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  overflow-y: auto;
  flex: 1;
}

/* 结果卡片 — Apple 风格 */
.result-card {
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  box-shadow: var(--card-shadow);
  cursor: pointer;
  transition: all 220ms cubic-bezier(0.22, 1, 0.36, 1);
  animation: stagger-in 0.5s var(--ease-apple) both;
}

.result-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--card-shadow-hover);
}

.result-card-inner {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.result-card-inner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s var(--ease-apple);
}

.result-card:hover .result-card-inner img {
  transform: scale(1.05);
}

.result-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  color: var(--text-tertiary);
}

.result-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--space-lg) var(--space-md) var(--space-md);
  background: linear-gradient(to top, rgba(0, 0, 0, 0.45) 0%, transparent 100%);
  backdrop-filter: blur(8px);
  opacity: 0;
  transform: translateY(8px);
  transition: all 220ms var(--ease-apple);
}

.result-card:hover .result-overlay {
  opacity: 1;
  transform: translateY(0);
}

.result-name {
  color: #fff;
  font-size: var(--text-sm);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.result-date {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.7);
}

.result-score {
  font-size: var(--text-xs);
  color: #fff;
  background: var(--accent);
  padding: 1px 8px;
  border-radius: 100px;
  font-weight: 600;
}

.results-more {
  text-align: center;
  padding: var(--space-md);
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
