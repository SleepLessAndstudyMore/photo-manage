import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSystemStore = defineStore('system', () => {
  const status = ref<any>(null)
  const tasks = ref<any[]>([])
  const loading = ref(false)

  async function fetchStatus() {
    try {
      const { data } = await (await import('@/api/system')).getSystemStatus()
      status.value = data
    } catch {
      // ignore
    }
  }

  async function fetchTasks() {
    try {
      const { data } = await (await import('@/api/system')).getTasks()
      tasks.value = data.items ?? []
    } catch {
      // ignore
    }
  }

  return { status, tasks, loading, fetchStatus, fetchTasks }
})
