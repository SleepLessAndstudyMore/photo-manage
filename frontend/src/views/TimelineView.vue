<template>
  <div class="timeline-page">
    <aside class="timeline-sidebar">
      <h3 class="sidebar-title">时间轴</h3>
      <div v-if="!timeline" class="sidebar-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="timeline.years.length === 0" class="sidebar-empty">
        暂无照片
      </div>
      <div v-else class="timeline-tree">
        <div v-for="y in timeline.years" :key="y.year" class="year-group">
          <div
            class="year-item"
            :class="{ active: selectedYear === y.year && !selectedMonth }"
            @click="toggleYear(y.year)"
          >
            <el-icon class="expand-icon" :class="{ expanded: expandedYears.has(y.year) }">
              <ArrowRight />
            </el-icon>
            <span class="year-label">{{ y.year }}</span>
            <span class="year-count">{{ y.count }}</span>
          </div>
          <div v-if="expandedYears.has(y.year)" class="months-list">
            <div v-for="m in y.months" :key="m.month" class="month-group">
              <div
                class="month-item"
                :class="{ active: selectedYear === y.year && selectedMonth === m.month && !selectedDay }"
                @click="toggleMonth(y.year, m.month)"
              >
                <span class="month-label">{{ m.month }} 月</span>
                <span class="month-count">{{ m.count }}</span>
              </div>
              <div v-if="expandedMonths.has(`${y.year}-${m.month}`)" class="days-list">
                <div
                  v-for="d in m.days"
                  :key="d.day"
                  class="day-item"
                  :class="{ active: selectedYear === y.year && selectedMonth === m.month && selectedDay === d.day }"
                  @click="selectDay(y.year, m.month, d.day)"
                >
                  <span>{{ d.day }} 日</span>
                  <span class="day-count">{{ d.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
    <main class="timeline-content">
      <div class="content-header">
        <h2 class="content-title" v-if="selectedYear">
          <span class="title-year">{{ selectedYear }}</span>
          <template v-if="selectedMonth"><span class="title-sep">/</span>{{ selectedMonth }}</template>
          <template v-if="selectedDay"><span class="title-sep">/</span>{{ selectedDay }}</template>
        </h2>
        <h2 class="content-title" v-else>
          <span class="title-year">全部照片</span>
        </h2>
        <span class="photo-total">{{ total }} 张照片</span>
      </div>
      <PhotoGrid
        :photos="photos"
        :loading="loading"
        empty-text="选择一个日期查看照片"
        @photo-click="onPhotoClick"
        @load-more="onLoadMore"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import { usePhotoStore } from '@/stores/photo'
import type { Photo } from '@/types/photo'
import PhotoGrid from '@/components/PhotoGrid.vue'

const router = useRouter()
const photoStore = usePhotoStore()

const expandedYears = ref<Set<number>>(new Set())
const expandedMonths = ref<Set<string>>(new Set())
const selectedYear = ref<number | null>(null)
const selectedMonth = ref<number | null>(null)
const selectedDay = ref<number | null>(null)

const timeline = computed(() => photoStore.timeline)
const photos = computed(() => photoStore.photos)
const total = computed(() => photoStore.total)
const loading = computed(() => photoStore.loading)

onMounted(async () => {
  await photoStore.fetchTimeline()
  await photoStore.fetchPhotos({ page: 1, page_size: 50 })
})

function toggleYear(year: number) {
  if (expandedYears.value.has(year)) {
    expandedYears.value.delete(year)
  } else {
    expandedYears.value.add(year)
  }
}

function toggleMonth(year: number, month: number) {
  const key = `${year}-${month}`
  if (expandedMonths.value.has(key)) {
    expandedMonths.value.delete(key)
  } else {
    expandedMonths.value.add(key)
  }
}

async function selectDay(year: number, month: number, day: number) {
  selectedYear.value = year
  selectedMonth.value = month
  selectedDay.value = day
  await photoStore.fetchPhotos({ year, month, day, page: 1, page_size: 50 })
}

function onPhotoClick(photo: Photo) {
  router.push(`/photos/${photo.id}`)
}

async function onLoadMore() {
  await photoStore.loadMore()
}
</script>

<style scoped>
.timeline-page {
  display: flex;
  height: 100%;
}

.timeline-sidebar {
  width: 240px;
  min-width: 240px;
  overflow-y: auto;
  padding: var(--space-lg) var(--space-md);
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid var(--border-color);
}

[data-theme="dark"] .timeline-sidebar {
  background: rgba(255, 255, 255, 0.03);
}

.sidebar-title {
  margin: 0 0 var(--space-lg);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-loading, .sidebar-empty {
  padding: var(--space-lg) 0;
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.timeline-tree {
  font-size: var(--text-sm);
}

.year-item, .month-item, .day-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  gap: var(--space-xs);
  transition: all var(--transition-fast);
  font-weight: 400;
}

.year-item:hover, .month-item:hover, .day-item:hover {
  background: var(--accent-light);
}

.year-item.active, .month-item.active, .day-item.active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}

.expand-icon {
  font-size: var(--text-xs);
  transition: transform var(--transition-fast);
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.year-label, .month-label {
  flex: 1;
}

.year-count, .month-count, .day-count {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  font-variant-numeric: tabular-nums;
}

.months-list {
  padding-left: var(--space-md);
}

.days-list {
  padding-left: var(--space-md);
}

.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: var(--space-xl) var(--space-lg) var(--space-md);
  display: flex;
  align-items: baseline;
  gap: var(--space-lg);
  flex-shrink: 0;
}

.content-title {
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: 200;
  letter-spacing: -1px;
  color: var(--text-primary);
}

.title-year {
  font-weight: 300;
}

.title-sep {
  margin: 0 4px;
  color: var(--text-tertiary);
  font-weight: 200;
}

.photo-total {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
}
</style>
