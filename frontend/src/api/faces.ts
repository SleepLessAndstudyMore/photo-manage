import client from './client'

export function getFaceClusters(params?: Record<string, unknown>) {
  return client.get('/faces/clusters', { params })
}

export function getFaceClusterDetail(id: number) {
  return client.get(`/faces/clusters/${id}`)
}

export function getFaceClusterPhotos(id: number, params?: Record<string, unknown>) {
  return client.get(`/faces/clusters/${id}/photos`, { params })
}

export function updateFaceCluster(id: number, data: Record<string, unknown>) {
  return client.put(`/faces/clusters/${id}`, data)
}

export function mergeFaceClusters(data: { cluster_ids: number[] }) {
  return client.post('/faces/clusters/merge', data)
}

export function splitFaceCluster(id: number, data: { face_ids: number[] }) {
  return client.post(`/faces/clusters/${id}/split`, data)
}

export function detectFaces() {
  return client.post('/faces/detect')
}

export function clusterFaces() {
  return client.post('/faces/cluster')
}
