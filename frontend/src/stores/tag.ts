import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTagStore = defineStore('tag', () => {
  const tags = ref<any[]>([])
  const loading = ref(false)

  async function fetchTags() {
    loading.value = true
    try {
      const { data } = await (await import('@/api/tags')).getTags()
      tags.value = data.items ?? []
    } finally {
      loading.value = false
    }
  }

  return { tags, loading, fetchTags }
})
