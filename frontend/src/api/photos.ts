import client from './client'

export function getPhotos(params?: Record<string, unknown>) {
  return client.get('/photos', { params })
}

export function getPhoto(id: number) {
  return client.get(`/photos/${id}`)
}

export function getPhotoExif(id: number) {
  return client.get(`/photos/${id}/exif`)
}

export function updatePhoto(id: number, data: Record<string, unknown>) {
  return client.put(`/photos/${id}`, data)
}

export function searchPhotos(data: Record<string, unknown>) {
  return client.post('/photos/search', data)
}

export function getDuplicates(params?: Record<string, unknown>) {
  return client.get('/photos/duplicates', { params })
}

export function getGpsPhotos(params?: Record<string, unknown>) {
  return client.get('/photos/gps', { params })
}

export function streamVideo(id: number) {
  return client.get(`/photos/${id}/stream`)
}

export function deletePhotoFile(id: number) {
  return client.post(`/system/delete-photo/${id}`)
}

export function generateEmbeddings() {
  return client.post('/photos/embeddings')
}
