import client from './client'

export function getAlbums(params?: { page?: number; page_size?: number }) {
  return client.get('/albums', { params })
}

export function getAlbum(id: number) {
  return client.get(`/albums/${id}`)
}

export function createAlbum(data: { name: string; description?: string }) {
  return client.post('/albums', data)
}

export function updateAlbum(id: number, data: Record<string, unknown>) {
  return client.put(`/albums/${id}`, data)
}

export function deleteAlbum(id: number) {
  return client.delete(`/albums/${id}`)
}

export function getAlbumPhotos(id: number, params?: { page?: number; page_size?: number }) {
  return client.get(`/albums/${id}/photos`, { params })
}

export function addPhotosToAlbum(albumId: number, photoIds: number[]) {
  return client.post(`/albums/${albumId}/photos`, { photo_ids: photoIds })
}

export function removePhotoFromAlbum(albumId: number, photoId: number) {
  return client.delete(`/albums/${albumId}/photos/${photoId}`)
}
