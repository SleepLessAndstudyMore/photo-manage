<template>
  <div class="exif-panel">
    <div v-if="loading" class="loading-wrap">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="exif" class="exif-content">
      <!-- 区块1: 核心信息 -->
      <div class="exif-section">
        <div class="section-header" @click="toggleSection('core')">
          <h4 class="section-title">核心信息</h4>
          <svg
            class="section-arrow"
            :class="{ expanded: sections.core }"
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
        <Transition name="expand">
          <div v-show="sections.core" class="section-body">
            <div class="core-info">
              <div class="core-time">{{ formatDateTime(exif.date_taken) }}</div>
              <div class="core-camera">{{ exif.camera_model || '未知相机' }}</div>
              <div class="core-lens">{{ exif.lens_model || '未知镜头' }}</div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 区块2: 技术参数 -->
      <div class="exif-section">
        <div class="section-header" @click="toggleSection('tech')">
          <h4 class="section-title">技术参数</h4>
          <svg
            class="section-arrow"
            :class="{ expanded: sections.tech }"
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
        <Transition name="expand">
          <div v-show="sections.tech" class="section-body">
            <div class="tech-grid">
              <div class="tech-item">
                <span class="tech-label">光圈</span>
                <span class="tech-value tech-highlight">{{ exif.f_number ? `f/${exif.f_number}` : '-' }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">快门</span>
                <span class="tech-value tech-highlight">{{ exif.exposure_time || '-' }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">ISO</span>
                <span class="tech-value tech-highlight">{{ exif.iso || '-' }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">焦距</span>
                <span class="tech-value">{{ exif.focal_length ? `${exif.focal_length}mm` : '-' }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">尺寸</span>
                <span class="tech-value">{{ exif.width && exif.height ? `${exif.width} × ${exif.height}` : '-' }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">文件大小</span>
                <span class="tech-value">{{ formatFileSize(exif.file_size) }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">方向</span>
                <span class="tech-value">{{ formatOrientation(exif.orientation) }}</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">厂商</span>
                <span class="tech-value">{{ exif.camera_make || '-' }}</span>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 区块3: 位置信息 -->
      <div v-if="hasLocation" class="exif-section">
        <div class="section-header" @click="toggleSection('location')">
          <h4 class="section-title">位置信息</h4>
          <svg
            class="section-arrow"
            :class="{ expanded: sections.location }"
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
        <Transition name="expand">
          <div v-show="sections.location" class="section-body">
            <div class="location-map" @click="openMap">
              <img
                v-if="mapUrl"
                :src="mapUrl"
                alt="地图"
                loading="lazy"
              />
              <div v-else class="map-placeholder">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                <span>点击打开地图</span>
              </div>
            </div>
            <div class="location-coords">
              {{ exif.gps_latitude?.toFixed(6) }}, {{ exif.gps_longitude?.toFixed(6) }}
            </div>
          </div>
        </Transition>
      </div>

      <!-- 底部操作 -->
      <div class="exif-actions">
        <button class="exif-btn" @click="copyAll">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          复制 EXIF 信息
        </button>
      </div>
    </div>

    <div v-else class="empty-wrap">
      <span class="text-secondary">暂无 EXIF 数据</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { PhotoExif } from '@/types/photo'

const props = defineProps<{
  exif: PhotoExif | null
  loading?: boolean
}>()

const sections = ref({
  core: true,
  tech: true,
  location: true,
})

function toggleSection(name: 'core' | 'tech' | 'location') {
  sections.value[name] = !sections.value[name]
}

const hasLocation = computed(() => {
  return props.exif?.gps_latitude != null && props.exif?.gps_longitude != null
})

const mapUrl = computed(() => {
  if (!hasLocation.value) return ''
  const lat = props.exif!.gps_latitude
  const lng = props.exif!.gps_longitude
  // 使用 OpenStreetMap 静态地图
  return `https://static-maps.openstreetmap.org/?center=${lat},${lng}&zoom=14&size=400x240&markers=${lat},${lng}`
})

function formatFileSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  if (bytes >= 1024) return (bytes / 1024).toFixed(0) + ' KB'
  return bytes + ' B'
}

function formatOrientation(val: number): string {
  const map: Record<number, string> = {
    1: '正常',
    2: '水平翻转',
    3: '旋转 180°',
    4: '垂直翻转',
    5: '顺时针 90° + 水平翻转',
    6: '顺时针 90°',
    7: '逆时针 90° + 水平翻转',
    8: '逆时针 90°',
  }
  return map[val] || `未知 (${val})`
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return '未知拍摄时间'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    weekday: 'long',
  })
}

function copyAll() {
  if (!props.exif) return
  const e = props.exif
  const text = [
    `拍摄时间: ${formatDateTime(e.date_taken)}`,
    `相机: ${e.camera_model || '未知'}`,
    `镜头: ${e.lens_model || '未知'}`,
    `光圈: ${e.f_number ? `f/${e.f_number}` : '-'}`,
    `快门: ${e.exposure_time || '-'}`,
    `ISO: ${e.iso || '-'}`,
    `焦距: ${e.focal_length ? `${e.focal_length}mm` : '-'}`,
    `尺寸: ${e.width && e.height ? `${e.width} × ${e.height}` : '-'}`,
    `文件大小: ${formatFileSize(e.file_size)}`,
  ].join('\n')
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('EXIF 信息已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

function openMap() {
  if (!hasLocation.value) return
  const lat = props.exif!.gps_latitude
  const lng = props.exif!.gps_longitude
  window.open(`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=16/${lat}/${lng}`, '_blank')
}
</script>

<style scoped>
.exif-panel {
  padding: var(--space-4) 0;
}

.exif-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

/* ===== 折叠区块 ===== */
.exif-section {
  border-bottom: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) 0;
  cursor: pointer;
  user-select: none;
  transition: color var(--transition-fast);
}

.section-header:hover {
  color: var(--accent);
}

.section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-arrow {
  color: var(--text-placeholder);
  transition: transform 0.2s var(--ease-standard);
}

.section-arrow.expanded {
  transform: rotate(180deg);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s var(--ease-standard);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}

/* ===== 核心信息 ===== */
.core-info {
  padding-bottom: var(--space-4);
}

.core-time {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.core-camera {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.core-lens {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* ===== 技术参数网格 ===== */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
  padding-bottom: var(--space-4);
}

.tech-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tech-label {
  font-size: 12px;
  color: var(--text-placeholder);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.tech-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.tech-highlight {
  color: var(--accent);
  font-weight: 600;
}

/* ===== 位置信息 ===== */
.location-map {
  width: 100%;
  height: 120px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--gray-100);
  cursor: pointer;
  margin-bottom: var(--space-2);
  position: relative;
}

.location-map img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.location-map::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 60%, rgba(0, 0, 0, 0.3));
  pointer-events: none;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  color: var(--text-placeholder);
}

.location-coords {
  font-size: 12px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
  padding-bottom: var(--space-4);
}

/* ===== 底部操作 ===== */
.exif-actions {
  padding-top: var(--space-4);
}

.exif-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.exif-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.loading-wrap,
.empty-wrap {
  padding: var(--space-lg) 0;
  text-align: center;
}

.empty-wrap .text-secondary {
  color: var(--text-secondary);
}
</style>
