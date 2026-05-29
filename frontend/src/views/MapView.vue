<template>
  <div class="view-map">
    <div class="map-header">
      <h2>地图视图</h2>
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

    <!-- Photo preview popup -->
    <el-dialog v-model="previewVisible" :title="previewPhoto?.file_name || ''" width="auto" destroy-on-close>
      <img
        v-if="previewPhoto?.thumbnail_path"
        :src="`/thumbnails/${previewPhoto.thumbnail_path}`"
        class="preview-image"
      />
      <div v-else class="preview-placeholder">暂无预览</div>
      <template #footer>
        <el-button size="small" @click="goToPhoto(previewPhoto?.id)">查看详情</el-button>
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
const previewVisible = ref(false)
const previewPhoto = ref<GpsPhoto | null>(null)

let mapInstance: any = null
let markersLayer: any = null
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

  mapInstance = L.map(mapEl.value, {
    center: [35, 105],
    zoom: 4,
    zoomControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(mapInstance)

  // Add markers with clustering
  const mcg = L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
  })

  allPhotos.forEach((p) => {
    const marker = L.marker([p.latitude, p.longitude], {
      title: p.file_name,
    })
    marker.bindPopup(`
      <div style="text-align:center;min-width:120px">
        <img src="/thumbnails/${p.thumbnail_path || ''}" style="width:120px;height:120px;object-fit:cover;border-radius:4px" /><br/>
        <small>${p.file_name}</small>
      </div>
    `)
    marker.on('click', () => {
      previewPhoto.value = p
      previewVisible.value = true
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
  gap: var(--space-md);
  padding: var(--space-md) var(--space-xl);
  flex-shrink: 0;
}
.map-header h2 {
  margin: 0;
  font-size: var(--text-2xl);
}
.map-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.map-container {
  flex: 1;
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin: 0 var(--space-xl) var(--space-xl);
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
}
.preview-image {
  max-width: 400px;
  max-height: 400px;
  border-radius: var(--radius-sm);
}
.preview-placeholder {
  width: 300px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}
</style>
