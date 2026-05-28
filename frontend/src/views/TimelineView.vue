<template>
  <div class="timeline-page">
    <main class="timeline-content">
      <div class="content-header">
        <div class="header-left">
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
        <div class="header-right">
          <el-dropdown trigger="click" @command="onTimeFilterCommand">
            <button class="time-filter-btn">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              {{ selectedYear ? `${selectedYear}/${selectedMonth || ''}` : '全部时间' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu class="time-tree-dropdown">
                <div v-if="!timeline" class="tree-loading">
                  <el-skeleton :rows="3" animated />
                </div>
                <div v-else-if="timeline.years.length === 0" class="tree-empty">
                  暂无照片
                </div>
                <div v-else class="timeline-tree">
                  <div
                    class="tree-item"
                    :class="{ active: !selectedYear }"
                    @click="clearTimeFilter"
                  >
                    全部时间
                  </div>
                  <div v-for="y in timeline.years" :key="y.year" class="year-group">
                    <div
                      class="tree-item year-item"
                      :class="{ active: selectedYear === y.year && !selectedMonth }"
                      @click="toggleYear(y.year)"
                    >
                      <el-icon class="expand-icon" :class="{ expanded: expandedYears.has(y.year) }">
                        <ArrowRight />
                      </el-icon>
                      <span class="item-label">{{ y.year }}</span>
                      <span class="item-count">{{ y.count }}</span>
                    </div>
                    <div v-if="expandedYears.has(y.year) && y.months" class="months-list">
                      <template v-for="m in y.months" :key="m?.month">
                        <div
                          v-if="m"
                          class="tree-item month-item"
                          :class="{ active: selectedYear === y.year && selectedMonth === m.month && !selectedDay }"
                          @click="selectMonth(y.year, m.month)"
                        >
                          <span class="item-label">{{ m.month }} 月</span>
                          <span class="item-count">{{ m.count }}</span>
                        </div>
                        <div v-if="m && expandedMonths.has(`${y.year}-${m.month}`)" class="days-list">
                          <div
                            v-for="d in m.days"
                            :key="d.day"
                            class="tree-item day-item"
                            :class="{ active: selectedYear === y.year && selectedMonth === m.month && selectedDay === d.day }"
                            @click="selectDay(y.year, m.month, d.day)"
                          >
                            <span>{{ d.day }} 日</span>
                            <span class="item-count">{{ d.count }}</span>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
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
import { ArrowRight, ArrowDown } from '@element-plus/icons-vue'
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

async function selectMonth(year: number, month: number) {
  selectedYear.value = year
  selectedMonth.value = month
  selectedDay.value = null
  await photoStore.fetchPhotos({ year, month, page: 1, page_size: 50 })
}

async function selectDay(year: number, month: number, day: number) {
  selectedYear.value = year
  selectedMonth.value = month
  selectedDay.value = day
  await photoStore.fetchPhotos({ year, month, day, page: 1, page_size: 50 })
}

async function clearTimeFilter() {
  selectedYear.value = null
  selectedMonth.value = null
  selectedDay.value = null
  await photoStore.fetchPhotos({ page: 1, page_size: 50 })
}

function onTimeFilterCommand(command: string) {
  // 处理下拉菜单命令
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
  height: 100%;
  display: flex;
  flex-direction: column;
}

.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: var(--space-6) var(--space-6) var(--space-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: var(--space-4);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.content-title {
  margin: 0;
  font-size: var(--text-h1);
  font-weight: var(--font-weight-bold);
  letter-spacing: var(--tracking-tight);
  color: var(--text-primary);
}

.title-year {
  font-weight: var(--font-weight-bold);
}

.title-sep {
  margin: 0 var(--space-1);
  color: var(--text-tertiary);
  font-weight: var(--font-weight-regular);
}

.photo-total {
  color: var(--text-tertiary);
  font-size: var(--text-caption);
  font-variant-numeric: tabular-nums;
}

/* 时间筛选按钮 */
.time-filter-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-body);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.time-filter-btn:hover {
  border-color: var(--accent);
  background: var(--accent-light);
}

/* 下拉菜单中的时间树 */
:deep(.time-tree-dropdown) {
  max-height: 400px;
  overflow-y: auto;
  min-width: 200px;
}

.tree-loading, .tree-empty {
  padding: var(--space-4);
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--text-caption);
}

.timeline-tree {
  padding: var(--space-2);
}

.tree-item {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  gap: var(--space-2);
  transition: all var(--transition-fast);
  font-weight: var(--font-weight-regular);
}

.tree-item:hover {
  background: var(--gray-50);
}

.tree-item.active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: var(--font-weight-medium);
}

.expand-icon {
  font-size: var(--text-caption);
  transition: transform var(--transition-fast);
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.item-label {
  flex: 1;
}

.item-count {
  color: var(--text-tertiary);
  font-size: var(--text-caption);
  font-variant-numeric: tabular-nums;
}

.months-list {
  padding-left: var(--space-4);
}

.days-list {
  padding-left: var(--space-4);
}
</style>
