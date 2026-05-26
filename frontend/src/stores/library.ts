import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { LibrarySource, ScanProgress } from '@/types/library'
import { getLibraries, addLibrary, deleteLibrary, scanLibrary, checkConsistency } from '@/api/libraries'

export const useLibraryStore = defineStore('library', () => {
  const libraries = ref<LibrarySource[]>([])
  const loading = ref(false)
  const scanProgress = ref<Map<number, ScanProgress>>(new Map())

  async function fetchLibraries() {
    loading.value = true
    try {
      const { data } = await getLibraries()
      libraries.value = data.items ?? []
    } finally {
      loading.value = false
    }
  }

  async function add(name: string, path: string) {
    await addLibrary({ name, path })
    await fetchLibraries()
  }

  async function remove(id: number) {
    await deleteLibrary(id)
    await fetchLibraries()
  }

  async function triggerScan(id: number) {
    await scanLibrary(id)
  }

  async function triggerCheckConsistency(id: number) {
    await checkConsistency(id)
  }

  function updateScanProgress(libraryId: number, progress: number, message: string) {
    scanProgress.value.set(libraryId, { progress, message })
  }

  function clearScanProgress(libraryId: number) {
    scanProgress.value.delete(libraryId)
  }

  return {
    libraries, loading, scanProgress,
    fetchLibraries, add, remove, triggerScan, triggerCheckConsistency,
    updateScanProgress, clearScanProgress,
  }
})
