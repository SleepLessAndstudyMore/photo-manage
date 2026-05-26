import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as albumsApi from '@/api/albums'

export const useAlbumStore = defineStore('album', () => {
  const albums = ref<any[]>([])
  const loading = ref(false)

  async function fetchAlbums() {
    loading.value = true
    try {
      const { data } = await albumsApi.getAlbums({ page_size: 200 })
      albums.value = data.items ?? []
    } finally {
      loading.value = false
    }
  }

  return { albums, loading, fetchAlbums }
})
