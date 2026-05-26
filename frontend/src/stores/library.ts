import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLibraryStore = defineStore('library', () => {
  const libraries = ref<any[]>([])
  const loading = ref(false)

  async function fetchLibraries() {
    loading.value = true
    try {
      const { data } = await (await import('@/api/libraries')).getLibraries()
      libraries.value = data.items ?? []
    } finally {
      loading.value = false
    }
  }

  return { libraries, loading, fetchLibraries }
})
