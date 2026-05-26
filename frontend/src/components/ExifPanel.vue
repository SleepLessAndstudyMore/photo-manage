<template>
  <div class="exif-panel">
    <div class="exif-header">
      <h3>EXIF 信息</h3>
      <button class="pill-btn" @click="copyAll">复制全部</button>
    </div>
    <div v-if="loading" class="loading-wrap">
      <el-skeleton :rows="8" animated />
    </div>
    <div v-else-if="exif" class="exif-list">
      <div v-for="row in exifRows" :key="row.label" class="exif-row">
        <span class="exif-label">{{ row.label }}</span>
        <span class="exif-value">{{ row.value }}</span>
      </div>
    </div>
    <div v-else class="empty-wrap">
      <span class="text-secondary">暂无 EXIF 数据</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { PhotoExif } from '@/types/photo'

const props = defineProps<{
  exif: PhotoExif | null
  loading?: boolean
}>()

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

interface ExifRow {
  label: string
  value: string
}

const exifRows = computed<ExifRow[]>(() => {
  if (!props.exif) return []
  const e = props.exif
  const rows: ExifRow[] = [
    { label: '相机厂商', value: e.camera_make || '未知' },
    { label: '相机型号', value: e.camera_model || '未知' },
    { label: '镜头型号', value: e.lens_model || '未知' },
    { label: '光圈', value: e.f_number ? `f/${e.f_number}` : '未知' },
    { label: '快门速度', value: e.exposure_time || '未知' },
    { label: 'ISO', value: e.iso ? String(e.iso) : '未知' },
    { label: '焦距', value: e.focal_length ? `${e.focal_length}mm` : '未知' },
    {
      label: 'GPS',
      value: e.gps_latitude != null && e.gps_longitude != null
        ? `${e.gps_latitude.toFixed(4)}, ${e.gps_longitude.toFixed(4)}`
        : '未知',
    },
    { label: '拍摄时间', value: e.date_taken ? new Date(e.date_taken).toLocaleString('zh-CN') : '未知' },
    { label: '尺寸', value: e.width && e.height ? `${e.width} × ${e.height}` : '未知' },
    { label: '文件大小', value: formatFileSize(e.file_size) },
    { label: '方向', value: formatOrientation(e.orientation) },
  ]
  return rows
})

function copyAll() {
  if (!props.exif) return
  const text = exifRows.value.map(r => `${r.label}: ${r.value}`).join('\n')
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('EXIF 信息已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.exif-panel {
  padding: var(--space-sm) 0;
}

.exif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.exif-header h3 {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
}

.exif-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.exif-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--border-color);
}

.exif-label {
  flex-shrink: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  width: 70px;
}

.exif-value {
  text-align: right;
  font-size: var(--text-sm);
  color: var(--text-primary);
  word-break: break-all;
  font-weight: 450;
}

.loading-wrap, .empty-wrap {
  padding: var(--space-lg) 0;
  text-align: center;
}
</style>
