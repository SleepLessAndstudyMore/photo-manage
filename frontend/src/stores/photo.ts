import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Photo, PhotoDetail, PhotoExif, PhotoListParams, TimelineResponse, FolderListResponse } from '@/types/photo'
import { getPhotos, getPhoto, getPhotoExif, updatePhoto } from '@/api/photos'
import client from '@/api/client'

export const usePhotoStore = defineStore('photo', () => {
  const photos = ref<Photo[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentPage = ref(1)
  const currentParams = ref<PhotoListParams>({ page: 1, page_size: 50 })
  const currentPhoto = ref<PhotoDetail | null>(null)
  const currentExif = ref<PhotoExif | null>(null)
  const timeline = ref<TimelineResponse | null>(null)
  const folders = ref<FolderListResponse | null>(null)

  async function fetchPhotos(params?: PhotoListParams) {
    loading.value = true
    currentParams.value = { page: 1, page_size: 50, ...params }
    try {
      const { data } = await getPhotos(currentParams.value)
      photos.value = data.items ?? []
      total.value = data.total ?? 0
      currentPage.value = data.page ?? 1
    } finally {
      loading.value = false
    }
  }

  async function loadMore() {
    if (loading.value) return
    const nextPage = currentPage.value + 1
    loading.value = true
    try {
      const { data } = await getPhotos({ ...currentParams.value, page: nextPage, page_size: currentParams.value.page_size })
      photos.value.push(...(data.items ?? []))
      currentPage.value = data.page ?? nextPage
    } finally {
      loading.value = false
    }
  }

  async function fetchPhotoById(id: number) {
    const { data } = await getPhoto(id)
    currentPhoto.value = data
  }

  async function fetchExif(id: number) {
    const { data } = await getPhotoExif(id)
    currentExif.value = data
  }

  async function updateMetadata(id: number, update: { rating?: number; is_favorite?: boolean }) {
    const { data } = await updatePhoto(id, update)
    // Update in local list
    const idx = photos.value.findIndex(p => p.id === id)
    if (idx >= 0) {
      photos.value[idx] = { ...photos.value[idx], ...data }
    }
    if (currentPhoto.value?.id === id) {
      currentPhoto.value = { ...currentPhoto.value, ...data }
    }
  }

  async function fetchTimeline(library_id?: number) {
    const params: Record<string, string> = {}
    if (library_id !== undefined) params.library_id = String(library_id)
    const { data } = await client.get('/photos/timeline', { params })
    timeline.value = data
  }

  async function fetchFolders(library_id?: number) {
    const params: Record<string, string> = {}
    if (library_id !== undefined) params.library_id = String(library_id)
    const { data } = await client.get('/photos/folders', { params })
    folders.value = data
  }

  return {
    photos, total, loading, currentPage, currentParams,
    currentPhoto, currentExif, timeline, folders,
    fetchPhotos, loadMore, fetchPhotoById, fetchExif,
    updateMetadata, fetchTimeline, fetchFolders,
  }
})
