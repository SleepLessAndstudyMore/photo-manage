import client from './client'

export function getTags() {
  return client.get('/tags')
}

export function getTagPhotos(id: number) {
  return client.get(`/tags/${id}/photos`)
}

export function addPhotoTag(photoId: number, tagId: number) {
  return client.post(`/photos/${photoId}/tags`, { tag_id: tagId })
}

export function removePhotoTag(photoId: number, tagId: number) {
  return client.delete(`/photos/${photoId}/tags/${tagId}`)
}
