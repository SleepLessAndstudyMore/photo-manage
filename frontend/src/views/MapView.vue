<template>
  <div class="view-map">
    <div class="map-header">
      <h2 class="page-title">地图视图</h2>
      <span v-if="photoCount" class="map-count">{{ photoCount }} 张带位置的照片</span>
    </div>
    <div class="map-container">
      <div v-if="loading" class="map-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <p>加载地图中...</p>
      </div>
      <EmptyState
        v-else-if="!loading && allPhotos.length === 0"
        type="map"
        title="暂无带位置信息的照片"
        subtitle="照片的地理位置将显示在这里"
      />
      <div ref="mapEl" class="map-leaflet"></div>
      <div v-if="error" class="map-error">
        <p>{{ error }}</p>
      </div>
    </div>

    <!-- 聚合标记照片弹窗 -->
    <el-dialog v-model="popupVisible" :title="popupTitle" width="640px" top="8vh" destroy-on-close class="glass-dialog">
      <div v-if="popupPhotos.length === 0" class="popup-empty">暂无照片</div>
      <div v-else class="popup-grid">
        <div
          v-for="photo in popupPhotos"
          :key="photo.id"
          class="popup-photo-item"
          @click="goToPhoto(photo.id)"
        >
          <img
            v-if="photo.thumbnail_path"
            :src="`/thumbnails/${photo.thumbnail_path}`"
            :alt="photo.file_name"
          />
          <div v-else class="popup-placeholder">无预览</div>
        </div>
      </div>
      <template #footer>
        <button class="pill-btn" @click="popupVisible = false">关闭</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getGpsPhotos } from '@/api/photos'
import EmptyState from '@/components/EmptyState.vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

interface GpsPhoto {
  id: number
  file_name: string
  latitude: number
  longitude: number
  thumbnail_path: string | null
  date_taken: string | null
}

const router = useRouter()
const mapEl = ref<HTMLElement | null>(null)
const loading = ref(true)
const error = ref('')
const photoCount = ref(0)
const popupVisible = ref(false)
const popupPhotos = ref<GpsPhoto[]>([])
const popupTitle = ref('')

let mapInstance: any = null
let allPhotos: GpsPhoto[] = []

onMounted(async () => {
  await loadPhotos()
  await nextTick()
  initMap()
})

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
})

async function loadPhotos() {
  try {
    const { data } = await getGpsPhotos()
    allPhotos = data.items ?? []
    photoCount.value = allPhotos.length
  } catch (e: any) {
    error.value = '加载 GPS 照片失败: ' + (e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

function initMap() {
  if (!mapEl.value || allPhotos.length === 0) return

  // Fix default Leaflet icon paths
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'

  mapInstance = L.map(mapEl.value, {
    center: [35, 105],
    zoom: 4,
    zoomControl: true,
  })

  // 使用 CartoDB 浅色/深色瓦片
  const tileUrl = isDark
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

  L.tileLayer(tileUrl, {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd',
  }).addTo(mapInstance)

  // 自定义聚合标记样式
  const mcg = L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 60,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    iconCreateFunction: (cluster: any) => {
      const count = cluster.getChildCount()
      const size = count < 10 ? 36 : count < 100 ? 44 : 52
      return L.divIcon({
        html: `<div class="custom-cluster" style="
          width:${size}px;height:${size}px;
          background: linear-gradient(135deg, #6366F1, #8B5CF6);
          border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          color:#fff;font-weight:600;font-size:${count < 100 ? 13 : 11}px;
          box-shadow:0 2px 12px rgba(99,102,241,0.4);
          border:2px solid rgba(255,255,255,0.3);
        ">${count}</div>`,
        className: 'marker-cluster-custom',
        iconSize: L.point(size, size),
      })
    },
  })

  // 按位置分组照片
  const locationGroups = new Map<string, GpsPhoto[]>()
  allPhotos.forEach((p) => {
    const key = `${p.latitude.toFixed(3)},${p.longitude.toFixed(3)}`
    if (!locationGroups.has(key)) {
      locationGroups.set(key, [])
    }
    locationGroups.get(key)!.push(p)
  })

  locationGroups.forEach((photos, key) => {
    const [lat, lng] = key.split(',').map(Number)
    const marker = L.marker([lat, lng])
    marker.on('click', () => {
      popupPhotos.value = photos
      popupTitle.value = `该位置 ${photos.length} 张照片`
      popupVisible.value = true
    })
    mcg.addLayer(marker)
  })

  mapInstance.addLayer(mcg)

  if (allPhotos.length > 1) {
    mapInstance.fitBounds(mcg.getBounds().pad(0.1))
  } else {
    mapInstance.setView([allPhotos[0].latitude, allPhotos[0].longitude], 13)
  }
}

function goToPhoto(id?: number) {
  if (id) router.push(`/photos/${id}`)
}
</script>

<style scoped>
.view-map {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: var(--text-h1);
  font-weight: var(--font-weight-bold);
  letter-spacing: var(--tracking-tight);
}

.map-count {
  font-size: var(--text-caption);
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

.map-container {
  flex: 1;
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  margin: 0 var(--space-6) var(--space-6);
  overflow: hidden;
}

.map-leaflet {
  width: 100%;
  height: 100%;
}

.map-loading, .map-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 1000;
  gap: 8px;
  color: var(--text-secondary);
}

/* ===== 聚合标记弹窗照片网格 ===== */
.popup-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-3);
  max-height: 400px;
  overflow-y: auto;
  padding: var(--space-2);
}

.popup-photo-item {
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s var(--ease-standard), box-shadow 0.2s var(--ease-standard);
  background: var(--gray-100);
}

.popup-photo-item:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.popup-photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.popup-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  font-size: var(--text-caption);
}

.popup-empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-secondary);
}

/* ===== Leaflet 自定义样式 ===== */
:deep(.marker-cluster-custom) {
  background: transparent !important;
  border: none !important;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: var(--radius-md) !important;
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
}

:deep(.leaflet-popup-tip) {
  background: var(--bg-card) !important;
}

[data-theme="dark"] :deep(.leaflet-container) {
  background: #1a1a2e;
}
</style>
