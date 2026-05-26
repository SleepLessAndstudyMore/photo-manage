import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePhotoStore = defineStore('photo', () => {
  const photos = ref<any[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentPage = ref(1)

  async function fetchPhotos(page = 1, pageSize = 50) {
    loading.value = true
    try {
      const { data } = await (await import('@/api/photos')).getPhotos({ page, page_size: pageSize })
      photos.value = data.items ?? []
      total.value = data.total ?? 0
      currentPage.value = page
    } finally {
      loading.value = false
    }
  }

  return { photos, total, loading, currentPage, fetchPhotos }
})
