import client from './client'

export function getTags(params?: Record<string, unknown>) {
  return client.get('/tags', { params })
}

export function getTagPhotos(tagId: number, params?: Record<string, unknown>) {
  return client.get(`/tags/${tagId}/photos`, { params })
}

export function addPhotoTag(photoId: number, tagId: number) {
  return client.post(`/photos/${photoId}/tags`, { tag_id: tagId, source: 'manual' })
}

export function removePhotoTag(photoId: number, tagId: number) {
  return client.delete(`/photos/${photoId}/tags/${tagId}`)
}

export function createTag(data: { name: string; name_zh?: string }) {
  return client.post('/photos/0/tags', { ...data, source: 'manual' })
}

export function deleteTag(tagId: number) {
  return client.delete(`/tags/${tagId}`)
}

export function updateTag(tagId: number, data: Record<string, unknown>) {
  return client.put(`/tags/${tagId}`, data)
}
