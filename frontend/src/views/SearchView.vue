<template>
  <div class="view-search">
    <div class="search-header">
      <h2>搜索</h2>
      <div class="search-header-actions">
        <div class="search-mode-tabs">
          <el-radio-group v-model="searchMode" size="small">
            <el-radio-button value="structured">结构化搜索</el-radio-button>
            <el-radio-button value="hybrid">自然语言搜索</el-radio-button>
          </el-radio-group>
        </div>
        <el-button size="small" text :loading="embeddingLoading" @click="onGenerateEmbeddings">
          生成向量
        </el-button>
      </div>
    </div>

    <div class="search-body">
      <!-- Hybrid search -->
      <template v-if="searchMode === 'hybrid'">
        <div class="hybrid-input-row">
          <el-input
            v-model="hybridQuery"
            placeholder="例如：去年在海边的猫、今年旅行拍的照片..."
            size="large"
            clearable
            @keyup.enter="doSearch"
          />
          <el-button type="primary" size="large" :loading="searching" @click="doSearch">
            搜索
          </el-button>
        </div>
        <div class="search-hint">
          <span>试试: "去年在海边的猫", "今年旅行", "最近7天的照片"</span>
        </div>
      </template>

      <!-- Structured search -->
      <template v-else>
        <div class="structured-filters">
          <el-form :inline="true" :model="structuredFilters" label-width="80px">
            <el-form-item label="文件名">
              <el-input v-model="structuredFilters.file_name" placeholder="模糊搜索" clearable />
            </el-form-item>
            <el-form-item label="相机型号">
              <el-input v-model="structuredFilters.camera_model" placeholder="如: Sony A7M4" clearable />
            </el-form-item>
            <el-form-item label="镜头">
              <el-input v-model="structuredFilters.lens_model" placeholder="如: FE 24-70mm" clearable />
            </el-form-item>
            <el-form-item label="日期从">
              <el-date-picker v-model="structuredFilters.date_from" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="日期至">
              <el-date-picker v-model="structuredFilters.date_to" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="标签">
              <el-select v-model="structuredFilters.tag_ids" multiple clearable placeholder="选择标签" style="width: 200px">
                <el-option v-for="tag in allTags" :key="tag.id" :label="tag.name_zh || tag.name" :value="tag.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="最低评分">
              <el-rate v-model="structuredFilters.rating_min" :max="5" />
            </el-form-item>
            <el-form-item label="收藏">
              <el-switch v-model="structuredFilters.is_favorite" />
            </el-form-item>
            <el-form-item label="逻辑">
              <el-radio-group v-model="structuredFilters.logic">
                <el-radio value="AND">与</el-radio>
                <el-radio value="OR">或</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="searching" @click="doSearch">搜索</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <!-- Search results -->
      <div class="search-results">
        <div v-if="!searched" class="results-placeholder">
          <el-icon :size="48"><Search /></el-icon>
          <p>输入搜索条件开始查找照片</p>
        </div>

        <div v-else-if="searching" class="results-loading">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="results.length === 0" class="results-empty">
          <el-icon :size="48"><Search /></el-icon>
          <p>未找到匹配的照片</p>
        </div>

        <template v-else>
          <div class="results-header">
            <span>找到 {{ total }} 张照片</span>
            <el-radio-group v-model="sortBy" size="small" @change="doSearch">
              <el-radio-button value="date_taken">日期</el-radio-button>
              <el-radio-button value="rating">评分</el-radio-button>
              <el-radio-button value="file_name">名称</el-radio-button>
            </el-radio-group>
          </div>
          <div class="results-grid">
            <div
              v-for="photo in results"
              :key="photo.id"
              class="result-item"
              @click="goToPhoto(photo.id)"
            >
              <img
                v-if="photo.thumbnail_path"
                :src="`/thumbnails/${photo.thumbnail_path}`"
                :alt="photo.file_name"
              />
              <div v-else class="result-placeholder">
                <el-icon><PictureFilled /></el-icon>
              </div>
              <div class="result-info">
                <span class="result-name">{{ photo.file_name }}</span>
                <div class="result-meta">
                  <span v-if="photo.date_taken" class="result-date">
                    {{ formatDate(photo.date_taken) }}
                  </span>
                  <span v-if="searchMode === 'hybrid' && photo.similarity_score != null" class="result-score">
                    {{ (photo.similarity_score * 100).toFixed(0) }}% 匹配
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="hasMore" class="results-more">
            <el-button text @click="loadMore">加载更多</el-button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Search, PictureFilled } from '@element-plus/icons-vue'
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
  // 首次进入自动触发搜索
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
  height: calc(100vh - 52px);
  display: flex;
  flex-direction: column;
  padding: 20px;
}
.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.search-header h2 { margin: 0; }
.search-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.search-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.hybrid-input-row {
  display: flex;
  gap: 12px;
}
.search-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-secondary, #999);
}
.structured-filters {
  padding: 16px;
  background: var(--color-bg-secondary, #fafafa);
  border-radius: 8px;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.search-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.results-placeholder, .results-loading, .results-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary, #999);
  gap: 12px;
}
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
}
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  overflow-y: auto;
  flex: 1;
}
.result-item {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-secondary, #f5f5f5);
  transition: transform 0.15s, box-shadow 0.15s;
}
.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.result-item img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}
.result-placeholder {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}
.result-info {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.result-name {
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.result-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.result-date {
  font-size: 11px;
  color: var(--color-text-secondary, #999);
}
.result-score {
  font-size: 11px;
  color: var(--color-primary, #7EC8C8);
  font-weight: 500;
  background: var(--color-primary-light, #e6f7f7);
  padding: 1px 6px;
  border-radius: 4px;
}
.results-more {
  text-align: center;
  padding: 12px;
  flex-shrink: 0;
}
</style>
