import { ref, onUnmounted } from 'vue'
import { defineStore } from 'pinia'
import type { SystemStatus, TaskInfo, SystemConfig } from '@/types/system'
import { getSystemStatus, getSystemConfig, updateSystemConfig, getTasks } from '@/api/system'
import { useWebSocket } from '@/composables/useWebSocket'

export const useSystemStore = defineStore('system', () => {
  const status = ref<SystemStatus | null>(null)
  const tasks = ref<TaskInfo[]>([])
  const config = ref<SystemConfig>({
    scan_interval: 300,
    page_size_default: 50,
    thumbnail_quality: 80,
    watchdog_enabled: false,
  })
  const loading = ref(false)
  const wsConnected = ref(false)

  let _unsubWs: (() => void) | null = null

  function connectWs() {
    const ws = useWebSocket()
    ws.connect()
    wsConnected.value = ws.isConnected.value
    _unsubWs = ws.onMessage((msg) => {
      if (msg.data.library_id != null) {
        if (msg.data.status === 'completed') {
          fetchStatus()
          fetchLibrariesAndPhotos()
        }
      }
    })
  }

  async function fetchLibrariesAndPhotos() {
    try {
      const { useLibraryStore } = await import('@/stores/library')
      const { usePhotoStore } = await import('@/stores/photo')
      useLibraryStore().fetchLibraries()
      usePhotoStore().fetchPhotos()
    } catch { /* ignore circular import issues */ }
  }

  function disconnectWs() {
    _unsubWs?.()
    _unsubWs = null
  }

  async function fetchStatus() {
    loading.value = true
    try {
      const { data } = await getSystemStatus()
      status.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchTasks() {
    try {
      const { data } = await getTasks()
      tasks.value = data.items ?? []
    } catch { /* ignore */ }
  }

  async function fetchConfig() {
    try {
      const { data } = await getSystemConfig()
      config.value = data
    } catch { /* use defaults */ }
  }

  async function updateConfig(update: Partial<SystemConfig>) {
    await updateSystemConfig(update as Record<string, unknown>)
    await fetchConfig()
  }

  onUnmounted(disconnectWs)

  return {
    status, tasks, config, loading, wsConnected,
    connectWs, disconnectWs, fetchStatus, fetchTasks, fetchConfig, updateConfig,
  }
})
