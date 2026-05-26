import client from './client'

export function getPhotos(params?: { page?: number; page_size?: number }) {
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

export function getDuplicates() {
  return client.get('/photos/duplicates')
}

export function streamVideo(id: number) {
  return client.get(`/photos/${id}/stream`)
}
