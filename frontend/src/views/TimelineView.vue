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
            <span class="year-label">{{ y.year }} 年</span>
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
        <h2 v-if="selectedYear">
          {{ selectedYear }} 年
          <template v-if="selectedMonth">{{ selectedMonth }} 月</template>
          <template v-if="selectedDay">{{ selectedDay }} 日</template>
        </h2>
        <h2 v-else>全部照片</h2>
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
  height: calc(100vh - 52px);
}
.timeline-sidebar {
  width: 260px;
  min-width: 260px;
  overflow-y: auto;
  border-right: 1px solid var(--color-border, #e8e8e8);
  padding: 16px;
  background: var(--color-bg-secondary, #fafafa);
}
.sidebar-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
}
.sidebar-loading, .sidebar-empty {
  padding: 20px 0;
  text-align: center;
  color: var(--color-text-secondary, #999);
}
.timeline-tree {
  font-size: 13px;
}
.year-item, .month-item, .day-item {
  display: flex;
  align-items: center;
  padding: 5px 8px;
  border-radius: 4px;
  cursor: pointer;
  gap: 4px;
}
.year-item:hover, .month-item:hover, .day-item:hover {
  background: var(--color-bg-hover, #f0f0f0);
}
.year-item.active, .month-item.active, .day-item.active {
  background: var(--color-primary-light, #e6f7f7);
  color: var(--color-primary, #7EC8C8);
  font-weight: 600;
}
.expand-icon {
  font-size: 12px;
  transition: transform 0.2s;
}
.expand-icon.expanded {
  transform: rotate(90deg);
}
.year-label, .month-label {
  flex: 1;
}
.year-count, .month-count, .day-count {
  color: var(--color-text-tertiary, #bbb);
  font-size: 11px;
}
.months-list {
  padding-left: 16px;
}
.days-list {
  padding-left: 16px;
}
.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.content-header {
  padding: 16px 20px 8px;
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-shrink: 0;
}
.content-header h2 {
  margin: 0;
  font-size: 18px;
}
.photo-total {
  color: var(--color-text-secondary, #999);
  font-size: 13px;
}
</style>
